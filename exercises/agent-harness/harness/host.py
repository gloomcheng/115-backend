"""The one chain every request goes through.

Validate, authorize, append, replay. In that order, every time, for every
route.

Unit 12 is about middleware, and the reason middleware exists in a service
like this one is exactly this: a rule that lives inside one handler is a
rule that the next handler will forget. Putting the steps in one object
means there is one place where the order is written down, and adding a
route cannot skip a step.

The order is not arbitrary:

1. Validate. A request that does not match the declared shape is not
   answerable, so it is refused before any work is done for it.
2. Authorize. Knowing who is asking does not mean they may do this.
3. Append. The write happens only after the first two passed.
4. Replay. What is true now is computed from the log, never kept beside
   it, so the two cannot drift apart.
"""

from typing import Any, Optional

from harness.authz import AuthError, Principal, require_role, verify_token
from harness.events import Event, EventLog
from harness.state import TaskState, replay
from harness.tools import ToolContext, ToolError, ToolRegistry, build_default_registry
from harness.validation import ToolCallIn, ToolResultIn


class Host:
    """The harness, as one object with one chain."""

    def __init__(self, log: EventLog, secret: bytes) -> None:
        self.log = log
        self.secret = secret
        self.tools: ToolRegistry = build_default_registry()

    # -- step 2: authorize ------------------------------------------------

    def authenticate(self, authorization: Optional[str], required_role: str = "reader") -> Principal:
        """Turn an Authorization header into a principal.

        A missing header and a bad token are both answered with 401, and
        both carry a reason that says which one it was, because "who are
        you" and "your token is wrong" are different problems.
        """
        if not authorization:
            raise AuthError(401, "missing Authorization header")
        if not authorization.startswith("Bearer "):
            raise AuthError(401, "Authorization header must use the Bearer scheme")
        return verify_token(authorization[len("Bearer ") :], self.secret, required_role)

    # -- step 3: append ---------------------------------------------------

    def _meta(self, principal: Principal, trace_id: Optional[str]) -> dict[str, Any]:
        """The host's own bookkeeping about one event.

        Kept out of the payload so that a reader can always tell the
        caller's data from the host's notes about it.
        """
        meta: dict[str, Any] = {"subject": principal.subject, "role": principal.role}
        if trace_id:
            meta["trace_id"] = trace_id
        return meta

    def record_tool_result(
        self,
        payload: dict[str, Any],
        principal: Principal,
        trace_id: Optional[str] = None,
    ) -> Event:
        """Validate, authorize, then append one tool result.

        This is the only way an event enters the log.
        """
        result = ToolResultIn.model_validate(payload)
        require_role(principal, "writer")
        return self.log.append("tool_result", result.model_dump(), meta=self._meta(principal, trace_id))

    def invoke_tool(
        self,
        call: ToolCallIn,
        principal: Principal,
        trace_id: Optional[str] = None,
    ) -> Event:
        """Run a tool and record what came back.

        A tool that fails is recorded as a failure. That is different from
        a result that never matched the declared shape: the shape check
        happens before anything is written, while an execution failure is
        a fact about the world and belongs in the log.
        """
        require_role(principal, "writer")
        context = ToolContext(principal=principal, host=self)

        try:
            details = self.tools.invoke(call, context)
            is_error = False
        except ToolError as exc:
            details = exc.details
            is_error = True

        payload = {
            "tool_call_id": call.tool_call_id,
            "tool_name": call.tool_name,
            "is_error": is_error,
            "details": details,
        }
        return self.record_tool_result(payload, principal, trace_id)

    # -- step 4: replay ---------------------------------------------------

    def state(self, principal: Principal) -> TaskState:
        """Compute the current state by replaying the log."""
        require_role(principal, "reader")
        return replay(self.log.read())
