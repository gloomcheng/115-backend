"""Lesson 02 — what a multipart body actually is on the wire.

    python multipart_demo.py show      # print the raw body, byte by byte
    python multipart_demo.py boundary  # what the boundary is for
    python multipart_demo.py parse     # reading it back without a framework
    python multipart_demo.py filename  # the part that is attacker-controlled
    python multipart_demo.py all

Run the server for the live half:

    python multipart_demo.py serve

then, with two different routes on purpose:

    curl -s -F "note=hello" -F "file=@README.md" http://127.0.0.1:8011/raw
    curl -s -F "note=hello" -F "file=@README.md" http://127.0.0.1:8011/upload

/raw declares no form parameters, so the framework hands the bytes over
untouched and the server prints them. /upload declares them, so the
framework parses first and returns fields instead. That difference is the
lesson.
"""

import sys

# The four modes below print things and need nothing installed. FastAPI is
# imported only by `serve`, so the wire format can be studied on a machine
# with no dependencies at all.


# --- part 1: the bytes ---------------------------------------------------


def show() -> None:
    print("1. A multipart body, exactly as it travels")
    print()
    print("   ------------------------------------------------------------------")
    print("   POST /upload HTTP/1.1")
    print("   Host: 127.0.0.1:8011")
    print('   Content-Type: multipart/form-data; boundary=----abc123')
    print()
    print("   ------abc123")
    print('   Content-Disposition: form-data; name="note"')
    print()
    print("   hello")
    print("   ------abc123")
    print('   Content-Disposition: form-data; name="file"; filename="a.txt"')
    print("   Content-Type: text/plain")
    print()
    print("   file contents go here")
    print("   ------abc123--")
    print("   ------------------------------------------------------------------")
    print()
    print("   Four things to notice, and none of them is JSON:")
    print("     1. the boundary in the header must match the lines in the body")
    print("     2. every part carries its own headers, then a blank line, then data")
    print("     3. the last boundary has two trailing dashes: that is the terminator")
    print("     4. a part can be binary; the delimiters must survive it untouched")


def boundary() -> None:
    print("2. Why a boundary exists at all")
    print()
    print("   JSON needs no delimiter. This is well defined:")
    print('     {"note": "hello", "count": 3}')
    print("        ^     ^        ^")
    print("   The parser knows a string starts at a quote and ends at the next")
    print("   quote, so it can tell where one value ends and the next begins.")
    print()
    print("   A file has no such rule. It can be any bytes at all, including:")
    print("     newlines, quotes, braces, a line that looks like a header,")
    print("     and 200 MB of a JPEG with no particular structure.")
    print()
    print("   So the sender invents a string that does not occur in the data, and")
    print("   writes it between the parts. That is the entire job of a boundary.")
    print()
    print("   Consequence worth remembering: a body containing the boundary string")
    print("   cannot be parsed, which is why servers pick something unguessable.")


def parse() -> None:
    print("3. Reading it back, without any framework")
    print()
    body = (
        b"------abc123\r\n"
        b'Content-Disposition: form-data; name="note"\r\n'
        b"\r\n"
        b"hello\r\n"
        b"------abc123\r\n"
        b'Content-Disposition: form-data; name="file"; filename="a.txt"\r\n'
        b"Content-Type: text/plain\r\n"
        b"\r\n"
        b"line one\r\nline two\r\n"
        b"------abc123--\r\n"
    )
    delimiter = b"------abc123"
    print(f"   body is {len(body)} bytes")
    print(f"   delimiter is {delimiter!r}")
    print()
    chunks = body.split(delimiter)
    print(f"   split gives {len(chunks)} pieces, and the first and last are empty:")
    print(f"     [0] {chunks[0]!r}")
    print(f"     [-1] {chunks[-1]!r}")
    print()
    for chunk in chunks[1:-1]:
        # The part ends with CRLF because the boundary must start on a new line.
        chunk = chunk.lstrip(b"\r\n")
        if chunk.endswith(b"\r\n"):
            chunk = chunk[:-2]
        raw_headers, _, data = chunk.partition(b"\r\n\r\n")
        print("   part:")
        for header in raw_headers.split(b"\r\n"):
            key, _, value = header.partition(b": ")
            print(f"     {key.decode()}: {value.decode()}")
        print(f"     data: {data!r}")
        print()


def filename() -> None:
    print("4. The one field you must never trust")
    print()
    print('   filename="a.txt"          <- fine')
    print('   filename="../../../etc/passwd"   <- the header said so')
    print()
    print("   Content-Disposition comes from the Client. It is text the Client")
    print("   chose, not a fact about a file on your disk.")
    print()
    print("   So this is wrong:")
    print("     path = UPLOAD_DIR / upload.filename      # traversal, straight up")
    print()
    print("   And this is right:")
    print("     path = UPLOAD_DIR / (uuid4().hex + suffix)")
    print()
    print("   The stored name is generated by the server and the suffix is taken")
    print("   from the client only after being reduced to an extension.")
    print()
    print("   The lesson from unit 08 applies: the value that arrives from outside")
    print("   is data, not an instruction, no matter which header it arrived in.")


def build_app():
    from fastapi import FastAPI, File, Form, Request, UploadFile

    api = FastAPI(title="Lesson 02 multipart")

    # Two routes, on purpose. Declaring Form/File makes the framework read
    # and consume the body, so request.body() then raises "Stream consumed".
    # Seeing the bytes therefore requires a route that declares nothing.

    @api.post("/raw")
    async def raw_body(request: Request):
        body = await request.body()
        content_type = request.headers.get("content-type", "")
        boundary = content_type.split("boundary=")[-1]
        print("--- raw body as received ---")
        print(body.decode("utf-8", errors="replace"))
        print("--- end ---", flush=True)
        return {
            "bytes": len(body),
            "boundary": boundary,
            "parts": len([p for p in body.split(boundary.encode()) if p.strip(b"\r\n-")]),
        }

    @api.post("/upload")
    async def upload(note: str = Form(...), file: UploadFile = File(...)):
        data = await file.read()
        return {
            "note": note,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_bytes": len(data),
            "stored_as": "a name the server generated, never the client's",
        }

    return api


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "show": show,
        "boundary": boundary,
        "parse": parse,
        "filename": filename,
    }
    if mode == "all":
        for runner in runners.values():
            runner()
    elif mode in runners:
        runners[mode]()
    elif mode == "serve":
        import uvicorn

        uvicorn.run(build_app(), host="127.0.0.1", port=8011, log_level="warning")
    else:
        print(f"unknown mode: {mode}")
        print(f"try one of: {', '.join(runners)}, serve")
        sys.exit(1)


if __name__ == "__main__":
    main()