"""Week 10, harness track: the event log and the check in front of it.

Start the service:

    fastapi dev main.py --port 8010

Send a tool result and watch it become an event:

    curl -i -X POST http://127.0.0.1:8010/events/tool-result \
      -H 'Content-Type: application/json' \
      -d '{"tool_call_id":"call_1","tool_name":"todowrite","details":{"todos":[{"content":"write the replay tests","status":"pending"}]}}'

Send the same result with a field missing and watch it refuse:

    curl -i -X POST http://127.0.0.1:8010/events/tool-result \
      -H 'Content-Type: application/json' \
      -d '{"tool_name":"todowrite"}'

Read the log back:

    curl -s http://127.0.0.1:8010/events
"""

import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, status

from harness.events import EventLog
from harness.validation import ToolResultIn

LOG_PATH = Path(os.environ.get("HARNESS_LOG", "events.jsonl"))
log = EventLog(LOG_PATH)

app = FastAPI(title="Agent Harness — week 10")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


@app.post("/events/tool-result", status_code=status.HTTP_201_CREATED)
def record_tool_result(body: ToolResultIn) -> dict[str, Any]:
    """Record one tool result as an event.

    The shape is checked by the model on the way in, so a malformed result
    never reaches this function and never reaches the log. The log only ever
    holds events that were accepted.
    """
    event = log.append("tool_result", body.model_dump())
    return event.to_dict()


@app.get("/events")
def list_events() -> dict[str, Any]:
    events = log.read()
    return {"count": len(events), "events": [event.to_dict() for event in events]}
