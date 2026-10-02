"""Lesson 10 — where validation happens decides what the client sees.

Run it on its own port:

    fastapi dev main.py --port 8003

Then send the same bad body to the two routes and compare the errors:

    curl -i -X POST http://127.0.0.1:8003/strict \\
      -H 'Content-Type: application/json' -d '{"role":"student"}'

    curl -i -X POST http://127.0.0.1:8003/loose \\
      -H 'Content-Type: application/json' -d '{"role":"student"}'
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Lesson 10 Validation")


class UserStrict(BaseModel):
    # Field constraints are declared here, so they run before the handler.
    name: str = Field(min_length=1, max_length=40)
    role: str | None = Field(default=None, max_length=20)


class Tags(BaseModel):
    label: str
    weight: int


class PostStrict(BaseModel):
    title: str
    tags: list[Tags]


@app.post("/strict")
def create_strict(payload: UserStrict):
    # Nothing here can raise for bad input: the framework already refused it.
    return {"name": payload.name, "role": payload.role, "source": "strict"}


@app.post("/loose")
def create_loose(body: dict):
    # The framework had nothing to check against, so every check is here,
    # after the handler has already started running.
    if "name" not in body or not body["name"]:
        raise HTTPException(status_code=422, detail="name is required")
    if len(body["name"]) > 40:
        raise HTTPException(status_code=422, detail="name must be 40 characters or fewer")
    return {"name": body["name"], "role": body.get("role"), "source": "loose"}


@app.post("/post-strict")
def create_post(payload: PostStrict):
    # A list of objects gives the error a location with an index in it.
    return {"title": payload.title, "tags": len(payload.tags)}