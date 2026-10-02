"""Lesson 08 — CRUD over SQLite, wired to HTTP.

Run it next to the practice API on a different port:

    fastapi dev main.py --port 8002

Then create, read, update, delete, and delete again:

    curl -i http://127.0.0.1:8002/users
    curl -i -X POST http://127.0.0.1:8002/users \\
      -H 'Content-Type: application/json' -d '{"name":"iris"}'
    curl -i http://127.0.0.1:8002/users/iris
    curl -i -X PUT http://127.0.0.1:8002/users/iris \\
      -H 'Content-Type: application/json' -d '{"name":"iris","role":"student"}'
    curl -i -X DELETE http://127.0.0.1:8002/users/iris
    curl -i -X DELETE http://127.0.0.1:8002/users/iris
"""

import sqlite3

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

DB_PATH = "users.db"

app = FastAPI(title="Lesson 08 CRUD")


class UserIn(BaseModel):
    name: str
    role: str | None = None


def connect():
    return sqlite3.connect(DB_PATH)


def ensure_table():
    connection = connect()
    connection.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        " name TEXT PRIMARY KEY NOT NULL,"
        " role TEXT)"
    )
    connection.commit()
    connection.close()


@app.on_event("startup")
def startup():
    ensure_table()


def row_to_user(row):
    return {"name": row[0], "role": row[1]}


@app.get("/users")
def list_users():
    connection = connect()
    rows = connection.execute("SELECT name, role FROM users ORDER BY name").fetchall()
    connection.close()
    return [row_to_user(row) for row in rows]


@app.get("/users/{name}")
def read_user(name: str):
    connection = connect()
    row = connection.execute("SELECT name, role FROM users WHERE name = ?", (name,)).fetchone()
    connection.close()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return row_to_user(row)


@app.post("/users", status_code=201)
def create_user(payload: UserIn):
    connection = connect()
    try:
        connection.execute(
            "INSERT INTO users (name, role) VALUES (?, ?)",
            (payload.name, payload.role),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        connection.close()
        raise HTTPException(status_code=409, detail="User already exists")
    connection.close()
    return {"name": payload.name, "role": payload.role}


@app.put("/users/{name}")
def replace_user(name: str, payload: UserIn):
    connection = connect()
    cursor = connection.execute(
        "UPDATE users SET name = ?, role = ? WHERE name = ?",
        (payload.name, payload.role, name),
    )
    connection.commit()
    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")
    connection.close()
    return {"name": payload.name, "role": payload.role}


@app.patch("/users/{name}")
def update_user(name: str, payload: dict):
    updates = {key: value for key, value in payload.items() if key in {"name", "role"}}
    if not updates:
        raise HTTPException(status_code=422, detail="No supported field to update")
    assignments = ", ".join(f"{column} = ?" for column in updates)
    connection = connect()
    cursor = connection.execute(
        f"UPDATE users SET {assignments} WHERE name = ?",
        (*updates.values(), name),
    )
    connection.commit()
    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")
    row = connection.execute(
        "SELECT name, role FROM users WHERE name = ?", (name,)
    ).fetchone()
    connection.close()
    return row_to_user(row)


@app.delete("/users/{name}")
def delete_user(name: str):
    connection = connect()
    cursor = connection.execute("DELETE FROM users WHERE name = ?", (name,))
    connection.commit()
    connection.close()
    return Response(status_code=204)