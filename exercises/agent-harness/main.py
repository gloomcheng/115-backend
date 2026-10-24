"""The harness service.

It started in unit 10 as a validation check in front of an event log. By the
final project it is the whole loop: authenticate, authorize, record,
replay, and hand a checkpoint to whoever picks the work up next.

Start it:

    fastapi dev main.py --port 8010

Mint a token first, because from unit 11 on, nothing is accepted without
one:

    export HARNESS_SECRET='test-secret-not-for-production'
    export TOKEN=$(python -m harness.authz alice admin)

Record a tool result:

    curl -i -X POST http://127.0.0.1:8010/events/tool-result \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d '{"tool_call_id":"call_1","tool_name":"todowrite","details":{"todos":[{"content":"write the replay tests","status":"pending"}]}}'

Read the state back:

    curl -s http://127.0.0.1:8010/state -H "Authorization: Bearer $TOKEN"
"""

import os
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

from harness.authz import AuthError, Principal, issue_token
from harness.checkpoint import Checkpoint
from harness.events import EventLog
from harness.host import Host
from harness.trace import TRACE_HEADER, normalize_trace_id
from harness.validation import ToolCallIn, ToolResultIn

LOG_PATH = Path(os.environ.get("HARNESS_LOG", "events.jsonl"))

# The signing key. A deployment sets it; a local run may fall back to the
# development value below, and that fallback is loud on purpose.
DEFAULT_DEV_SECRET = "test-secret-not-for-production"
SECRET = os.environ.get("HARNESS_SECRET", DEFAULT_DEV_SECRET).encode()
if "HARNESS_SECRET" not in os.environ:
    print(
        "warning: HARNESS_SECRET is not set, using the development value. "
        "Do not do this on a machine other people can reach.",
        file=sys.stderr,
    )

log = EventLog(LOG_PATH)
host = Host(log, SECRET)

app = FastAPI(title="Agent Harness")


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    """Give every request one id, and hand it back in the response header.

    The id is the same one that lands in the metadata of every event the
    request produces, so one number ties a response to the log entries it
    caused.
    """
    trace_id = normalize_trace_id(request.headers.get(TRACE_HEADER))
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers[TRACE_HEADER] = trace_id
    return response


def current_principal(
    authorization: Optional[str] = Header(default=None),
) -> Principal:
    """Who is asking."""
    try:
        return host.authenticate(authorization)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.reason) from exc


def require_writer(principal: Principal = Depends(current_principal)) -> Principal:
    """Only a writer may change the log."""
    if not principal.can("writer"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"role '{principal.role}' cannot write events",
        )
    return principal


def require_admin(principal: Principal = Depends(current_principal)) -> Principal:
    """Only an admin may mint tokens."""
    if not principal.can("admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"role '{principal.role}' cannot mint tokens",
        )
    return principal


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/tokens", status_code=status.HTTP_201_CREATED)
def mint_token(
    subject: str,
    role: str = "reader",
    ttl_seconds: int = 3600,
    principal: Principal = Depends(require_admin),
) -> dict[str, Any]:
    """Mint a token for somebody else.

    The caller has to be an admin, which is why the first token is minted
    from the command line instead of from here.
    """
    try:
        token = issue_token(subject, role, SECRET, ttl_seconds=ttl_seconds)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.reason) from exc
    return {"token": token, "subject": subject, "role": role, "issued_by": principal.subject}


@app.post("/events/tool-result", status_code=status.HTTP_201_CREATED)
def record_tool_result(
    request: Request,
    body: ToolResultIn,
    principal: Principal = Depends(require_writer),
) -> dict[str, Any]:
    """Record one tool result as an event.

    The shape is checked before this function runs, so a malformed result
    never reaches the log. The log only ever holds events that were
    accepted.
    """
    event = host.record_tool_result(body.model_dump(), principal, request.state.trace_id)
    return event.to_dict()


@app.get("/events")
def list_events(principal: Principal = Depends(current_principal)) -> dict[str, Any]:
    events = log.read()
    return {"count": len(events), "events": [event.to_dict() for event in events]}


@app.get("/state")
def read_state(principal: Principal = Depends(current_principal)) -> dict[str, Any]:
    """The state, computed by replaying the log."""
    return host.state(principal).to_dict()


@app.get("/tools")
def list_tools(principal: Principal = Depends(current_principal)) -> dict[str, Any]:
    """The catalogue of tools the agent can call."""
    return {"tools": host.tools.describe()}


@app.post("/tools", status_code=status.HTTP_201_CREATED)
def call_tool(
    request: Request,
    call: ToolCallIn,
    principal: Principal = Depends(require_writer),
) -> dict[str, Any]:
    """Call one tool and record what came back.

    A tool that fails is recorded as a failure. That is different from a
    result that never matched the declared shape: the shape check happens
    before anything is written, while an execution failure is a fact about
    the world and belongs in the log.
    """
    event = host.invoke_tool(call, principal, request.state.trace_id)
    return event.to_dict()


@app.get("/checkpoint")
def read_checkpoint(
    goal: str = "continue the work",
    principal: Principal = Depends(current_principal),
) -> dict[str, Any]:
    """The checkpoint: prose that points at a structured appendix."""
    checkpoint = Checkpoint(goal=goal, state=host.state(principal))
    return {
        "prose": checkpoint.prose(),
        "appendix": checkpoint.appendix(),
        "rendered": checkpoint.render(),
    }
