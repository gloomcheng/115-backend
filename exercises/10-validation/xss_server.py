"""Lesson 10 — XSS: when validation passing stops meaning safe.

    python xss_server.py          # serves on 8009, open it in a browser
    python xss_server.py --check  # print the HTML each route returns and exit

The payload is the same one unit 10 already accepts with a 200:

    <script>alert(1)</script>

Routes:

    /raw?name=...     interpolated into the HTML body with no escaping
    /escaped?name=... the same page, html.escape() applied
    /naive-attr       an attribute, escaped with a function that forgets quotes
    /escaped-attr     the same attribute, quotes escaped too
    /url              a query string, escaped for the wrong context

Run it, log in at nothing, open http://127.0.0.1:8009/raw?name=<script>alert(1)</script>
and watch what the browser's address bar do.
"""

import html
import sys

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Lesson 10 XSS")

PAYLOAD = "<script>alert(1)</script>"


def naive_escape(value: str) -> str:
    """The escaping people write from memory: handle the angle brackets.

    It is not wrong about angle brackets. It is incomplete, and the gap is
    the quote character, which matters the moment the value lands in an
    attribute instead of the page body.
    """
    return value.replace("<", "&lt;").replace(">", "&gt;")


@app.get("/raw")
async def raw(name: str = "iris"):
    return HTMLResponse(
        f"<h1>profile</h1><p>name: {name}</p>"
        "<p>the value above came straight from the query string.</p>"
    )


@app.get("/escaped")
async def escaped(name: str = "iris"):
    return HTMLResponse(
        f"<h1>profile</h1><p>name: {html.escape(name)}</p>"
        "<p>same page, html.escape() applied. The browser shows the tags as text.</p>"
    )


@app.get("/naive-attr")
async def naive_attr(name: str = "iris"):
    return HTMLResponse(
        f"<h1>profile</h1><input value=\"{naive_escape(name)}\">"
        "<p>the angle brackets were escaped, the quotes were not.</p>"
    )


@app.get("/escaped-attr")
async def escaped_attr(name: str = "iris"):
    return HTMLResponse(
        f"<h1>profile</h1><input value=\"{html.escape(name, quote=True)}\">"
        "<p>quote=True also escapes the double quote, so the value cannot leave the attribute.</p>"
    )


@app.get("/url")
async def in_url(name: str = "iris"):
    return HTMLResponse(
        f"<h1>search</h1><p><a href=\"/next?also={html.escape(name)}\">next</a></p>"
        "<p>html.escape() is still the wrong tool in a URL. It stops the quote "
        "breaking out of the attribute, but &amp; inside a URL is not the same as "
        "&amp;amp; and a URL needs its own encoding.</p>"
    )


def check() -> int:
    """Print what each route actually returns, so the difference is visible
    without a browser. Run with --check."""
    import warnings

    warnings.filterwarnings("ignore")
    from fastapi.testclient import TestClient  # type: ignore[import-not-found]

    client = TestClient(app)
    probes = [
        ("/raw", {"name": PAYLOAD}),
        ("/escaped", {"name": PAYLOAD}),
        ("/naive-attr", {"name": '" onfocus=alert(1) x="'}),
        ("/escaped-attr", {"name": '" onfocus=alert(1) x="'}),
    ]
    for route, params in probes:
        body = client.get(route, params=params).text
        print(f"--- GET {route}  name={params['name']!r}")
        print(body)
        print()
    return 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8009, log_level="warning")