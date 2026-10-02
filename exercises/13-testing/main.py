"""Lesson 13 — a test earns its keep by failing when the code is wrong.

Run the tests:

    pytest -q

Then read main.py and tests/test_contract.py side by side. Every
assertion in the test file corresponds to one row of the contract table
that section 01 builds from a running server.
"""

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Lesson 13 Testing")

NOTES: dict[str, dict] = {"welcome": {"title": "Welcome", "body": "First note"}}


@app.get("/health")
def health():
    # The contract says this body is exactly {"ok": true}. Changing True to
    # the string "yes" keeps the route working and breaks every client that
    # reads the field. Only an assertion on the body can catch that.
    return {"ok": True}


@app.get("/notes")
def list_notes():
    return {"items": list(NOTES.values()), "count": len(NOTES)}


@app.get("/notes/{name}")
def get_note(name: str):
    if name not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")
    return NOTES[name]


@app.post("/notes", status_code=201)
def create_note(body: dict):
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="name is required")
    note = {"title": body.get("title", "Untitled"), "body": body.get("body", "")}
    NOTES[name] = note
    return {"name": name, **note}
