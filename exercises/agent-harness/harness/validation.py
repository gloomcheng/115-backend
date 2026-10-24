"""The boundary where an agent's tool result becomes an event.

Everything the agent runtime hands over is external input. It arrives with no
promise about its shape, so it is checked here, at the edge, before it is
allowed anywhere near the event log.

The rule this week: a result that fails the check never reaches the log. The
log only ever holds events that were accepted, so a reader of the log never
has to wonder whether a line is trustworthy.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ToolResultIn(BaseModel):
    """One tool result handed back by the agent runtime.

    `extra="forbid"` is deliberate. An unknown field is a sign that the
    sender and the receiver disagree about the contract, and a contract
    nobody agreed on is not a contract.
    """

    model_config = ConfigDict(extra="forbid")

    tool_call_id: str = Field(min_length=1, max_length=128)
    tool_name: str = Field(min_length=1, max_length=64)
    is_error: bool = False
    details: Optional[dict[str, Any]] = None


class EventIn(BaseModel):
    """One event the host wants to record."""

    model_config = ConfigDict(extra="forbid")

    op: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)


class ToolCallIn(BaseModel):
    """One tool call the agent runtime wants executed.

    A call and a result are two different shapes on purpose. The call asks
    for something; the result reports what happened. Mixing them is how a
    half-finished write ends up looking like a finished one.
    """

    model_config = ConfigDict(extra="forbid")

    tool_call_id: str = Field(min_length=1, max_length=128)
    tool_name: str = Field(min_length=1, max_length=64)
    arguments: dict[str, Any] = Field(default_factory=dict)
