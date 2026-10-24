"""Who may write events, and who may read state.

Unit 11 is about login and tokens. The same question arrives here in a
sharper form: a tool result handed over from outside is not automatically
allowed to become part of the harness's memory, and whoever is reading the
state back is not automatically allowed to read it.

The rule this unit: every request carries a role, and every write and
every read is checked against that role before it happens.

A token here is the same shape as a JWT: three parts, base64url, and an
HMAC signature over the first two. Nothing else. That is deliberately the
whole implementation, so the lesson is about the shape of the thing rather
than about the API of a library.

    header  .  payload  .  signature
    b64url  .  b64url   .  b64url(HMAC-SHA256)

The header says how the payload is signed. The payload says who and what.
The signature says nobody changed the payload in transit.
"""

import base64
import hashlib
import hmac
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

# Reading the state is the weakest thing you can do here. Writing an event
# is stronger, because a written event becomes part of the memory that every
# later replay is computed from.
ROLE_RANK: dict[str, int] = {"reader": 1, "writer": 2, "admin": 3}

ROLE_DESCRIPTIONS: dict[str, str] = {
    "reader": "read the replayed state, cannot write events",
    "writer": "write events and read the state",
    "admin": "everything a writer can do, plus mint new tokens",
}

TOKEN_HEADER = {"alg": "HS256", "typ": "HARNESS"}
DEFAULT_TTL_SECONDS = 3600


class AuthError(Exception):
    """A request was refused.

    `status` is the HTTP status the host should answer with. 401 means the
    caller could not prove who they are. 403 means they proved it, and the
    proof says they may not do this.
    """

    def __init__(self, status: int, reason: str) -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason


@dataclass(frozen=True)
class Principal:
    """Who is making the request, and what that person is allowed to do."""

    subject: str
    role: str

    def can(self, required: str) -> bool:
        return ROLE_RANK.get(self.role, 0) >= ROLE_RANK.get(required, 99)

    def to_dict(self) -> dict[str, str]:
        return {"subject": self.subject, "role": self.role}


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(signing_input: str, secret: bytes) -> bytes:
    return hmac.new(secret, signing_input.encode("ascii"), hashlib.sha256).digest()


def issue_token(
    subject: str,
    role: str,
    secret: bytes,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    now: Optional[float] = None,
) -> str:
    """Mint a token for a subject.

    The signature covers the header and the payload together, so a caller
    cannot swap the role out of a token they were given.
    """
    if role not in ROLE_RANK:
        raise AuthError(400, f"unknown role: {role}")
    issued_at = time.time() if now is None else now
    header = _b64url(json.dumps(TOKEN_HEADER, separators=(",", ":"), sort_keys=True).encode())
    payload = _b64url(
        json.dumps(
            {"sub": subject, "role": role, "exp": int(issued_at + ttl_seconds)},
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    )
    signature = _b64url(_sign(f"{header}.{payload}", secret))
    return f"{header}.{payload}.{signature}"


def verify_token(
    token: str,
    secret: bytes,
    required_role: str = "reader",
    now: Optional[float] = None,
) -> Principal:
    """Check a token and return the principal it stands for.

    The order of the checks matters. Malformed, then bad signature, then
    expired, then not allowed: each one is cheaper than the next, and the
    first three all mean the same thing to the caller, which is that the
    token is not usable.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError(401, "malformed token")

    header_b64, payload_b64, signature_b64 = parts

    expected = _sign(f"{header_b64}.{payload_b64}", secret)
    try:
        provided = _b64url_decode(signature_b64)
    except Exception as exc:  # noqa: BLE001 - any decoding failure is a bad token
        raise AuthError(401, "malformed token") from exc

    # compare_digest, not ==: a byte-by-byte comparison leaks how much of
    # the signature was guessed right, one byte at a time.
    if not hmac.compare_digest(expected, provided):
        raise AuthError(401, "bad signature")

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception as exc:  # noqa: BLE001
        raise AuthError(401, "malformed token") from exc

    current = time.time() if now is None else now
    expires_at = payload.get("exp")
    if not isinstance(expires_at, (int, float)) or current >= expires_at:
        raise AuthError(401, "token expired")

    subject = payload.get("sub")
    role = payload.get("role")
    if not isinstance(subject, str) or role not in ROLE_RANK:
        raise AuthError(401, "malformed token")

    principal = Principal(subject=subject, role=role)
    if not principal.can(required_role):
        raise AuthError(
            403,
            f"role '{role}' cannot {required_role}; "
            f"'{required_role}' needs one of: "
            + ", ".join(name for name, rank in ROLE_RANK.items() if rank >= ROLE_RANK[required_role]),
        )
    return principal


def require_role(principal: Principal, required_role: str) -> None:
    """Raise unless the principal is allowed to do something."""
    if not principal.can(required_role):
        raise AuthError(403, f"role '{principal.role}' cannot {required_role}")


def _main(argv: Optional[list[str]] = None) -> int:
    """Mint a token from the command line.

        python -m harness.authz <subject> <role> [ttl_seconds]

    The secret comes from the HARNESS_SECRET environment variable. This is
    the bootstrap path: an operator mints the first admin token by hand,
    and from then on the service mints the rest.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    subject = args[0]
    role = args[1] if len(args) > 1 else "admin"
    ttl = int(args[2]) if len(args) > 2 else DEFAULT_TTL_SECONDS

    secret = os.environ.get("HARNESS_SECRET")
    if not secret:
        print("HARNESS_SECRET is not set", file=sys.stderr)
        return 2

    try:
        print(issue_token(subject, role, secret.encode(), ttl_seconds=ttl))
    except AuthError as exc:
        print(exc.reason, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
