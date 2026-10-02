"""Lesson 04 — two ways the server side fails.

Start it next to the practice API:

    fastapi dev boom.py --port 8001

Then ask the two routes the same question, twice:

    curl -i 'http://127.0.0.1:8001/page?size=10'
    curl -i 'http://127.0.0.1:8001/page?size=abc'
    curl -i http://127.0.0.1:8001/boom

Neither request is malformed. The first pair is only interesting because of
where the conversion happens.
"""

from fastapi import FastAPI

app = FastAPI(title="Lesson 04 Server Failure")


@app.get("/page")
def page(size: int = 20):
    # FastAPI converts the query parameter before this function runs.
    # size=abc never reaches this line: the server answers 422 by itself.
    return {"size": size}


@app.get("/manual-page")
def manual_page(size: str = "20"):
    # No type annotation, so nothing is checked before this line.
    # The client error happens inside the handler and becomes a 500.
    return {"size": int(size)}


@app.get("/boom")
def boom():
    # This division raises ZeroDivisionError while the server is handling the request.
    # Nothing about the request was wrong; the handler itself is broken.
    return {"value": 1 / 0}