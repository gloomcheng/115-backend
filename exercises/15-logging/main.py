"""Lesson 15 — two logs, two jobs.

    fastapi dev main.py --port 8008

Section 02 needs a route that raises so you can compare what the access
log says with what the traceback says. Section 05 adds a second route that
touches the database, which is where "it works locally" stops being true.
"""

import logging
import time
from itertools import count

from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Lesson 15 Logging")

logger = logging.getLogger("notes")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s %(message)s",
)

USERS = {"iris": {"name": "iris", "role": "student"}}

ids = count(1)


@app.middleware("http")
async def assign_request_id(request: Request, call_next):
    # Section 04: this is the line that makes an application log line
    # joinable to an access log line. Without it, request_id is "-".
    request.state.request_id = f"r{next(ids):04d}"
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/users/{name}")
def get_user(name: str):
    if name not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS[name]


@app.get("/boom")
def boom():
    # Raises on purpose. The access log will record 500 for this request
    # and nothing else; the traceback goes to the terminal, unlinked.
    raise ValueError("something the handler could not handle")


@app.get("/slow")
def slow():
    # A route that is measurably slower, so duration in the access log has
    # something to say.
    time.sleep(0.4)
    return {"slept": 0.4}


@app.get("/users")
def list_users(request: Request):
    # One application log line, carrying the request id assigned by the
    # middleware in section 04.
    logger.info(
        "listing users count=%d request_id=%s",
        len(USERS),
        getattr(request.state, "request_id", "-"),
    )
    return {"items": list(USERS.values())}


@app.get("/admin")
def admin():
    # Logs the token, which is the mistake section 06 is about.
    logger.info("admin viewed with token=%s", "Bearer eyJhbGciOiJIUzI1NiJ9.demo")
    return {"admin_panel": True}
