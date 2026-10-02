"""Lesson 14 — the same mistake, four different contracts.

    fastapi dev main.py --port 8007

This server exposes the same note store twice: once as REST, once as
GraphQL. The point of the lesson is not that GraphQL is better. It is that
"the client asked for a field that does not exist" is answered completely
differently by each family, and you have to know which family you are
talking to before you can read an error.

gRPC and tRPC are not served here. They are contract files you read, not
endpoints you run, and section 05 handles that difference.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from graphql import GraphQLError, build_schema, graphql_sync

app = FastAPI(title="Lesson 14 API Families")

NOTES: dict[str, dict] = {
    "welcome": {"name": "welcome", "title": "Welcome", "tags": ["intro", "start"]},
    "api": {"name": "api", "title": "API design", "tags": ["rest"]},
}

# --- REST -------------------------------------------------------------


@app.get("/notes")
def list_notes():
    # Every field comes back, whether or not the client wanted it.
    return {"items": list(NOTES.values())}


@app.get("/notes/{name}")
def get_note(name: str):
    if name not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")
    return NOTES[name]


@app.post("/notes")
def create_note(body: dict):
    name = body.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="name is required")
    note = {"name": name, "title": body.get("title", "Untitled"), "tags": body.get("tags", [])}
    NOTES[name] = note
    return note


# --- GraphQL ----------------------------------------------------------

SCHEMA = build_schema(
    """
    type Note {
      name: String!
      title: String!
      tags: [String!]!
    }

    type Query {
      notes: [Note!]!
      note(name: String!): Note
    }
    """
)


def resolve_notes(_root, _info):
    return list(NOTES.values())


def resolve_note(_root, _info, name):
    return NOTES.get(name)


SCHEMA.query_type.fields["notes"].resolve = resolve_notes
SCHEMA.query_type.fields["note"].resolve = resolve_note


@app.post("/graphql")
async def graphql_endpoint(request: Request):
    payload = await request.json()
    result = graphql_sync(SCHEMA, payload.get("query"), variable_values=payload.get("variables"))

    # Note the status code: 200, even though the query was rejected.
    body = {"data": result.data}
    if result.errors:
        body["errors"] = [
            {"message": error.message, "path": error.path} for error in result.errors
        ]
    return JSONResponse(body, status_code=200)


@app.get("/graphql")
def graphql_playground_hint():
    return {
        "how_to_use": "POST a JSON body with a query field to this same path",
        "example": '{"query": "{ notes { name title } }"}',
    }
