"""Lesson 12 — CSRF, demonstrated rather than described.

Run two servers, because an attack needs two origins:

    python csrf_server.py victim 8006
    python csrf_server.py attacker 8007

Then open http://127.0.0.1:8007/ in a browser after logging in at
http://127.0.0.1:8006/login and watch what happens on the victim's server.

A third server shows the same request without a cookie, which is what
unit 11 and unit 12 already do:

    python csrf_server.py guarded 8010
    python csrf_server.py bearer 8008

The point of the whole file: the header scheme this course already uses
is not vulnerable, and the reason is structural, not because anybody
thought about it. Adding a cookie puts the vulnerability back.
"""

import hmac
import sys

from fastapi import FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse

PORT = {"victim": 8006, "guarded": 8010, "attacker": 8007, "bearer": 8008}

USERS = {"iris": {"password": "lesson", "role": "student"}}

victim = FastAPI(title="Lesson 12 CSRF victim")
guarded = FastAPI(title="Lesson 12 CSRF victim, defended")
attacker = FastAPI(title="Lesson 12 CSRF attacker")
bearer = FastAPI(title="Lesson 12 the scheme this course already uses")

ACTIONS: list[str] = []

# Not a secret and not committed anywhere meaningful; lesson material only.
CSRF_TOKEN = "lesson-12-csrf-token"
ALLOWED_ORIGIN = "http://127.0.0.1:8010"


def record(entry: str) -> None:
    ACTIONS.append(entry)
    print(f"[server] {entry}", flush=True)


# --- the victim: a normal session-cookie app ------------------------------


@victim.post("/login")
async def login(name: str = Form(...), password: str = Form(...)):
    account = USERS.get(name)
    if account is None or account["password"] != password:
        return HTMLResponse("no", status_code=401)
    response = HTMLResponse("logged in")
    # This is the ordinary way to write a session cookie. No SameSite, no
    # CSRF token, no Origin check. All three are discussed in section 08.4.
    response.set_cookie("session", name, httponly=True)
    return response


@victim.get("/")
async def victim_root(request: Request):
    who = request.cookies.get("session", "nobody")
    return HTMLResponse(
        f"<p>victim server. you are: <b>{who}</b></p>"
        f"<p>actions so far: {len(ACTIONS)}</p>"
    )


@victim.post("/transfer")
async def transfer(request: Request, amount: str = Form("100")):
    who = request.cookies.get("session")
    if who is None:
        record("transfer refused: no cookie")
        return HTMLResponse("no session", status_code=401)
    # No Origin check, no CSRF token. This is the vulnerability.
    record(f"TRANSFER {amount} from {who}")
    return HTMLResponse(f"ok, moved {amount} from {who}")


# --- the same app, defended three ways -----------------------------------


@guarded.post("/login")
async def guarded_login(name: str = Form(...), password: str = Form(...)):
    account = USERS.get(name)
    if account is None or account["password"] != password:
        return HTMLResponse("no", status_code=401)
    response = HTMLResponse("logged in")
    response.set_cookie("session", name, httponly=True, samesite="lax")
    # A token the attacker's page has never seen and cannot read.
    response.set_cookie("csrf", CSRF_TOKEN, httponly=False, samesite="lax")
    return response


@guarded.post("/transfer")
async def guarded_transfer(
    request: Request,
    amount: str = Form("100"),
    csrf: str = Form(""),
    origin: str | None = Header(default=None),
):
    who = request.cookies.get("session")
    if who is None:
        record("guarded refused: no cookie")
        return HTMLResponse("no session", status_code=401)

    # Defence 1: the Origin header is set by the browser and cannot be set
    # by the attacker's page. A cross-site POST from 8007 carries 8007.
    #
    # Note the shape: `origin and origin != ALLOWED`. A missing Origin is
    # allowed through to the token check rather than rejected here, because
    # non-browser clients do not send it. That is a real limitation, and
    # section 08.4 says what it means.
    if origin and origin != ALLOWED_ORIGIN:
        record(f"guarded refused on Origin: {origin}")
        return HTMLResponse("bad origin", status_code=403)

    # Defence 2: the token. SameSite=Lax stops the cookie on a cross-site
    # POST, and the token stops it even if that default ever changes.
    if not hmac.compare_digest(csrf, CSRF_TOKEN):
        record("guarded refused on CSRF token")
        return HTMLResponse("bad csrf token", status_code=403)

    record(f"guarded TRANSFER {amount} from {who}")
    return HTMLResponse(f"ok, moved {amount} from {who}")


# --- a browser sends these; the attacker's page cannot ---------------------


@attacker.get("/")
async def attacker_root():
    # A form with no JavaScript. The browser submits it and attaches the
    # victim's session cookie automatically, because that is what browsers
    # do with cookies on a cross-site POST.
    return HTMLResponse(
        """<h1>totally normal website</h1>
<form action="http://127.0.0.1:8006/transfer" method="post">
  <input type="hidden" name="amount" value="10000">
  <button type="submit">claim your prize</button>
</form>
<p>the button says one thing and the form posts to port 8006</p>"""
    )


@attacker.get("/guarded")
async def attacker_guarded():
    # Same form, pointed at the defended app. Note csrf="" — the page has no
    # way to learn the real token, because it is stored for 8006 only.
    return HTMLResponse(
        """<h1>totally normal website</h1>
<form action="http://127.0.0.1:8010/transfer" method="post">
  <input type="hidden" name="amount" value="10000">
  <input type="hidden" name="csrf" value="">
  <button type="submit">claim your prize</button>
</form>"""
    )


# --- the attacker: a different origin entirely ---------------------------


@attacker.get("/")
async def attacker_root():
    # A form with no JavaScript. The browser submits it and attaches the
    # victim's cookie automatically, because that is what browsers do with
    # cookies on a cross-site POST.
    return HTMLResponse(
        """<h1>totally normal website</h1>
<form action="http://127.0.0.1:8006/transfer" method="post">
  <input type="hidden" name="amount" value="10000">
  <button type="submit">claim your prize</button>
</form>
<p>the button says one thing and the form posts to port 8006</p>"""
    )


# --- the scheme this course already uses ---------------------------------


@bearer.post("/login")
async def bearer_login(name: str = Form(...), password: str = Form(...)):
    return {"access_token": name, "note": "returned to the caller, never stored by the browser"}


@bearer.post("/transfer")
async def bearer_transfer(authorization: str | None = Header(default=None)):
    # There is no cookie here. The only way in is this header, and a browser
    # will not attach a header to a cross-site form post, because only
    # JavaScript on this same origin can set it.
    if not authorization:
        record("bearer transfer with no header: refused")
        raise HTTPException(status_code=401, detail="Authorization header required")
    record(f"bearer transfer accepted for {authorization}")
    return {"ok": True}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "victim"
    port = PORT.get(mode, 8006)
    app = {"victim": victim, "guarded": guarded, "attacker": attacker, "bearer": bearer}[mode]
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()