"""Lesson 12 — middleware is a position in the request, not a feature.

The signing key comes from the environment, so it has to be supplied:

    SIGNING_KEY=lesson-12-key-a fastapi dev main.py --port 8005

Then look at what middleware sees, including a path that has no route:

    curl -i http://127.0.0.1:8005/nope
    curl -i http://127.0.0.1:8005/key-info

Issuing and verifying tokens is identical to unit 11 and is not repeated
here. What changes is where the role comes from.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from itertools import count

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

# The key is read from the environment. If it is missing, the app refuses to
# start rather than falling back to a value that would live in this file.
SIGNING_KEY = os.environ.get("SIGNING_KEY")
if not SIGNING_KEY:
    raise RuntimeError(
        "SIGNING_KEY is not set. A signing key belongs in the environment; "
        "hardcoding one here would put it in version control."
    )
KEY = SIGNING_KEY.encode()

USERS = {
    "iris": {"name": "iris", "role": "student"},
    "root": {"name": "root", "role": "admin"},
}

app = FastAPI(title="Lesson 12 Middleware")

CHALLENGE = {"WWW-Authenticate": 'Bearer realm="lesson-12"'}


def b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64decode(encoded: str) -> bytes:
    return base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))


def sign(payload: dict) -> str:
    header_part = b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload_part = b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = b64encode(
        hmac.new(KEY, f"{header_part}.{payload_part}".encode(), hashlib.sha256).digest()
    )
    return f"{header_part}.{payload_part}.{signature}"


def read_token(token: str) -> dict:
    try:
        header_part, payload_part, signature = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed token", headers=CHALLENGE)
    expected = b64encode(
        hmac.new(KEY, f"{header_part}.{payload_part}".encode(), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Bad signature", headers=CHALLENGE)
    payload = json.loads(b64decode(payload_part))
    if payload.get("exp", 0) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired", headers=CHALLENGE)
    return payload


def key_fingerprint() -> str:
    return hashlib.sha256(KEY).hexdigest()[:8]


ids = count(1)

# The LAST middleware registered below is the OUTERMOST one, so this pair is
# written inner-first. Swap the two blocks and trace_inner runs before
# request.state.trace exists: AttributeError, which becomes a 500.
@app.middleware("http")
async def trace_inner(request: Request, call_next):
    request.state.trace.append("inner:in")
    response = await call_next(request)
    request.state.trace.append("inner:out")
    return response


@app.middleware("http")
async def trace_outer(request: Request, call_next):
    request.state.trace = ["outer:in"]
    response = await call_next(request)
    request.state.trace.append("outer:out")
    response.headers["x-trace"] = " > ".join(request.state.trace)
    return response


# A second middleware with a real job: every request that reaches the process
# gets an id, including requests that never match a route.
@app.middleware("http")
async def assign_request_id(request: Request, call_next):
    request.state.request_id = f"r{next(ids):04d}"
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    return response


# A third middleware, and the first one that refuses work instead of only
# observing it. Registered last, so it is the OUTERMONE of all three: the
# limiter runs before the trace middlewares and before routing.
#
# The counter is per client key, and the window is fixed. Unit 12 section 08
# shows exactly what that costs at a window boundary.
# 30 per minute is deliberately generous: this app also carries the rest of
# unit 12's exercises, and a tight limit would hand students a 429 halfway
# through homework that has nothing to do with rate limiting. Lower it when
# you want to see the refusal sooner.
RATE_LIMIT = 30
RATE_WINDOW = 60.0
_hits: dict[str, tuple[int, float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - (now % RATE_WINDOW)
    count, seen_start = _hits.get(client, (0, window_start))
    if window_start != seen_start:
        count = 0
    if count >= RATE_LIMIT:
        retry_after = int(RATE_WINDOW - (now % RATE_WINDOW)) + 1
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"Retry-After": str(retry_after)},
        )
    _hits[client] = (count + 1, window_start)
    response = await call_next(request)
    response.headers["x-ratelimit-limit"] = str(RATE_LIMIT)
    response.headers["x-ratelimit-remaining"] = str(RATE_LIMIT - count - 1)
    return response


def current_subject(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing credentials", headers=CHALLENGE)
    return read_token(authorization.removeprefix("Bearer ").strip())["sub"]


def require_admin(subject: str = Depends(current_subject)) -> str:
    # The role is read from the server's own table, never from the token.
    if USERS[subject]["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return subject


class ProfileIn(BaseModel):
    # extra="forbid" turns a silent drop into a 422 that names the field.
    model_config = ConfigDict(extra="forbid")

    nickname: str


@app.get("/key-info")
def key_info():
    return {
        "key_fingerprint": key_fingerprint(),
        "source": "environment variable",
    }


@app.get("/open")
def open_route():
    return {"visible": "anyone may read this"}


@app.get("/profile")
def profile(subject: str = Depends(current_subject)):
    return {"sub": subject, "role": USERS[subject]["role"], "role_source": "server table"}


@app.get("/admin")
def admin(subject: str = Depends(require_admin)):
    return {"sub": subject, "admin_panel": True, "role_source": "server table"}


@app.post("/profile")
def update_profile(payload: ProfileIn, subject: str = Depends(current_subject)):
    return {"sub": subject, "nickname": payload.nickname}


@app.post("/login")
def login(body: dict):
    account = USERS.get(body.get("name", ""))
    if account is None or body.get("password") != "lesson":
        raise HTTPException(status_code=401, detail="Wrong name or password", headers=CHALLENGE)
    now = int(time.time())
    # The role claim below is deliberately wrong for root. Unit 11 read the
    # role out of the token; this app looks it up, so the wrong claim is inert.
    claimed_role = "intern" if account["role"] == "admin" else "student"
    return {
        "access_token": sign(
            {"sub": account["name"], "role": claimed_role, "exp": now + 3600},
        ),
        "token_type": "Bearer",
    }
