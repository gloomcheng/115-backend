from fastapi import FastAPI, HTTPException

app = FastAPI(title="HTTP Practice API")

# Observe who sends the request and where each status code is returned.
# GET 200 / POST 201 / missing resource 404 / invalid body 422

users = {"alice": {"name": "Alice", "note": "First HTTP example"}}


@app.get("/")
def root():
    return {"message": "Try GET /health"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/users/{name}")
def get_user(name: str):
    if name not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[name]


@app.post("/users", status_code=201)
def create_user(body: dict):
    # Keep validation explicit until the course introduces request models.
    if "name" not in body or not body["name"]:
        raise HTTPException(status_code=422, detail="name is required")
    name = body["name"]
    users[name] = body
    return body
