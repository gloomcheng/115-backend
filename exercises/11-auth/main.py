"""Lesson 11 — JWT is base64 plus an HMAC, and nothing else.

Run it on its own port:

    fastapi dev main.py --port 8004

Then log in and use the token:

    curl -i -X POST http://127.0.0.1:8004/login \\
      -H 'Content-Type: application/json' \\
      -d '{"name":"iris","role":"student"}'

    curl -i http://127.0.0.1:8004/private
    curl -i http://127.0.0.1:8004/private -H 'Authorization: Bearer <token>'
    curl -i http://127.0.0.1:8004/admin -H 'Authorization: Bearer <token>'
"""

import base64
import hashlib
import hmac
import json
import time

from fastapi import FastAPI, Header, HTTPException

# Not a real secret and not committed anywhere; lesson material only.
SECRET = b"lesson-11-demo-signing-key"

USERS = {
    "iris": {"name": "iris", "role": "student"},
    "root": {"name": "root", "role": "admin"},
}

app = FastAPI(title="Lesson 11 Auth")


def b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def b64decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(encoded + padding)


def sign(header: dict, payload: dict) -> str:
    header_part = b64encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = b64encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = b64encode(
        hmac.new(SECRET, f"{header_part}.{payload_part}".encode(), hashlib.sha256).digest()
    )
    return f"{header_part}.{payload_part}.{signature}"


def read_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Malformed token", headers=CHALLENGE)
    header_part, payload_part, signature = parts
    expected = b64encode(
        hmac.new(SECRET, f"{header_part}.{payload_part}".encode(), hashlib.sha256).digest()
    )
    # Compare in constant time so the check does not leak the expected value.
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Bad signature", headers=CHALLENGE)
    payload = json.loads(b64decode(payload_part))
    if payload.get("exp", 0) < int(time.time()):
        raise HTTPException(status_code=401, detail="Token expired", headers=CHALLENGE)
    return payload


CHALLENGE = {"WWW-Authenticate": 'Bearer realm="lesson-11"'}


def bearer(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing credentials", headers=CHALLENGE)
    return read_token(authorization.removeprefix("Bearer ").strip())


@app.post("/login")
def login(body: dict):
    account = USERS.get(body.get("name", ""))
    if account is None or body.get("password") != "lesson":
        raise HTTPException(status_code=401, detail="Wrong name or password", headers=CHALLENGE)
    now = int(time.time())
    return {
        "access_token": sign(
            {"alg": "HS256", "typ": "JWT"},
            {"sub": account["name"], "role": account["role"], "iat": now, "exp": now + 3600},
        ),
        "token_type": "Bearer",
        "expires_in": 3600,
    }


@app.get("/whoami")
def whoami(authorization: str | None = Header(default=None)):
    return read_token(bearer(authorization)["sub"] and bearer(authorization))


@app.get("/private")
def private(authorization: str | None = Header(default=None)):
    payload = bearer(authorization)
    return {"secret": "only a signed-in user sees this", "sub": payload["sub"]}


@app.get("/admin")
def admin(authorization: str | None = Header(default=None)):
    payload = bearer(authorization)
    # Authenticated. Now the separate question: is this user allowed?
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return {"admin_panel": True, "sub": payload["sub"]}


@app.post("/login-expired")
def login_expired(body: dict):
    # A token whose signature is perfectly valid but whose exp is in the past.
    past = int(time.time()) - 60
    return {
        "access_token": sign(
            {"alg": "HS256", "typ": "JWT"},
            {"sub": body.get("name", "iris"), "role": "student", "exp": past},
        )
    }