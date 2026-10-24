"""The tool call contract.

Unit 14 is about API families: the shapes a service speaks so that a caller
can predict what it gets back. The harness speaks one of those shapes, and
every tool the agent can reach is written against it.

A call is a request: a name, a call id, and arguments. A result is a
report: a call id, a name, an error flag, and details. The two shapes are
different on purpose. A call says what was asked for; a result says what
happened. Keeping them apart is what lets a failed write be recorded as a
failure instead of being mistaken for a write.

The registry is the whole point of the module. Adding a tool is adding an
entry, not adding a branch to the host. The host keeps speaking the same
contract to every one of them.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from harness.authz import Principal
from harness.validation import ToolCallIn

# The two failure modes are different and must not be confused.
#
# A shape failure is caught at the edge, before anything is recorded. That
# was unit 10's rule and it still holds.
#
# An execution failure is a tool that ran and failed. It is recorded, with
# is_error set, because "the tool failed" is a fact about what happened and
# the log is where facts live. It is still not state.
SHAPE_FAILURE = "shape_failure"
EXECUTION_FAILURE = "execution_failure"


class ToolError(Exception):
    """The call was well shaped, but the tool failed.

    `details` is what goes into the event. It has to carry the reason, or
    the log will show a failure nobody can explain.
    """

    def __init__(self, reason: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = details or {"error": reason}


@dataclass(frozen=True)
class ToolContext:
    """What a tool handler is allowed to see."""

    principal: Principal
    host: Any  # the Host; typed loosely to avoid an import cycle


@dataclass(frozen=True)
class ToolSpec:
    """The contract of one tool."""

    name: str
    description: str
    params_model: type[BaseModel]
    handler: Callable[[dict[str, Any], ToolContext], dict[str, Any]]


class TodoItemIn(BaseModel):
    """One item of the task list, as it arrives from the agent."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=400)
    status: str = Field(min_length=1, max_length=32)


class TodoListIn(BaseModel):
    """The whole task list, as it arrives from the agent."""

    model_config = ConfigDict(extra="forbid")

    todos: list[TodoItemIn] = Field(default_factory=list, max_length=200)


class NoArgumentsIn(BaseModel):
    """A tool that takes no arguments."""

    model_config = ConfigDict(extra="forbid")


class ToolRegistry:
    """Every tool the agent can reach, and the contract of each one."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> ToolSpec:
        if spec.name in self._tools:
            raise ValueError(f"tool already registered: {spec.name}")
        self._tools[spec.name] = spec
        return spec

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def describe(self) -> list[dict[str, Any]]:
        """The catalogue a caller reads before it calls anything."""
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "arguments": spec.params_model.model_json_schema(),
            }
            for spec in (self._tools[name] for name in self.names())
        ]

    def invoke(self, call: ToolCallIn, context: ToolContext) -> dict[str, Any]:
        """Run one tool and return the details of its result.

        Raises ToolError when the tool failed. The caller decides what to
        record; this function does not write anything.
        """
        spec = self._tools.get(call.tool_name)
        if spec is None:
            raise ToolError(
                f"unknown tool: {call.tool_name}",
                {"error": f"unknown tool: {call.tool_name}", "known_tools": self.names()},
            )

        try:
            params = spec.params_model.model_validate(call.arguments)
        except ValidationError as exc:
            raise ToolError(
                f"bad arguments for {call.tool_name}",
                {"error": f"bad arguments for {call.tool_name}", "problems": exc.error_count()},
            ) from exc

        try:
            return spec.handler(params.model_dump(), context)
        except ToolError:
            raise
        except Exception as exc:  # noqa: BLE001 - a tool must not take the host down
            raise ToolError(f"{call.tool_name} raised {type(exc).__name__}: {exc}") from exc


def build_default_registry() -> ToolRegistry:
    """The registry the host starts with.

    Two tools, because two is enough to show the shape of the contract:
    one that changes the task list, one that reads it back.
    """
    registry = ToolRegistry()

    def write_todos(arguments: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        todos = arguments.get("todos") or []
        return {"todos": todos}

    def read_state(arguments: dict[str, Any], context: ToolContext) -> dict[str, Any]:
        state = context.host.state(context.principal)
        return state.to_dict()

    registry.register(
        ToolSpec(
            name="todowrite",
            description="Replace the task list with the given todos.",
            params_model=TodoListIn,
            handler=write_todos,
        )
    )
    registry.register(
        ToolSpec(
            name="read_state",
            description="Read the replayed state back.",
            params_model=NoArgumentsIn,
            handler=read_state,
        )
    )
    return registry
