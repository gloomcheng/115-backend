"""Lesson 14 — WebSocket, from the bytes up.

    python websocket_demo.py key       # the handshake key and what it becomes
    python websocket_demo.py frame     # what a message looks like on the wire
    python websocket_demo.py serve     # a raw server on 8014, no dependencies

Then, in another terminal:

    python websocket_demo.py client    # speaks the protocol by hand

Nothing here uses a WebSocket library. The point is that the protocol is
about 40 lines of framing on top of HTTP, and you cannot debug it with a
library when the library is what is hiding the problem.
"""

import base64
import hashlib
import socket
import sys
import threading

PORT = 8014

# RFC 6455 section 1.3. This string is not secret and not chosen by anyone;
# it is the constant that turns a random key into a verifiable answer.
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def expected_accept(key: str) -> str:
    """base64(sha1(key + GUID)) — the whole of the server's proof."""
    return base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()


def show_key() -> None:
    print("1. The handshake, and the one piece of maths in it")
    print()
    print("   The Client sends a random key and asks to switch protocol:")
    print()
    print("     Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==")
    print("     Sec-WebSocket-Version: 13")
    print()
    print("   The Server answers 101 and returns a value derived from that key:")
    print()
    key = "dGhlIHNhbXBsZSBub25jZQ=="
    print(f"     sha1({key} + GUID) -> base64 = {expected_accept(key)}")
    print()
    print("   That value is RFC 6455's own worked example, and this program")
    print("   reproduces it without a library.")
    print()
    print("   What is it for? It proves the Server understood HTTP, not that it")
    print("   merely echoed a string back. An intermediary that does not parse")
    print("   HTTP cannot produce it. That is the entire authentication step,")
    print("   and notice there is no password anywhere in it.")


def show_frame() -> None:
    print("2. A message, and why you cannot just read until EOF")
    print()
    print("   An HTTP body says how long it is. This is that header:")
    print()
    print("     Content-Length: 317")
    print("     317 bytes follow, then the body is over.")
    print()
    print("   A WebSocket message carries its length in the first two bytes of")
    print("   the frame instead. Here is the frame for the text 'hi':")
    print()
    payload = b"hi"
    mask = b"\x01\x02\x03\x04"
    header = bytes([0x81, 0x80 | len(payload)])
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    # Pad to a fixed column so the three arrows line up. The lesson quotes this
    # output verbatim, and hand-counted spaces do not survive a length change.
    rows = [
        (header, "0x81 FIN+text, 0x82 length"),
        (mask, "masking key, chosen by the Client"),
        (masked, "payload, XORed with the key"),
    ]
    width = max(len(raw.hex(" ")) for raw, _ in rows)
    for raw, label in rows:
        print(f"     {raw.hex(' '):<{width}}    <- {label}")
    print()
    print("   Undo the XOR and the message comes back:")
    print(f"     {masked.hex(' ')} XOR {mask.hex(' ')} = {payload!r}")
    print()
    print("   Three things that have no equivalent in HTTP:")
    print("     - the length is 7 bits, or 7+16, or 7+64, chosen by the size")
    print("     - the Client must mask its bytes; a Server never does")
    print("     - there is no Content-Length and no EOF, so the connection stays open")
    print()
    print("   That last point is the one that breaks code. HTTP ends when the")
    print("   length is reached. A WebSocket has no end, so you have to read the")
    print("   frame header, decide how many bytes that frame is, and only then")
    print("   read that many. 'Read until the socket closes' will hang forever.")


# --- the raw server ------------------------------------------------------


def handle(connection: socket.socket, address) -> None:
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(4096)
        if not chunk:
            return
        data += chunk

    request = data.decode("utf-8", errors="replace")
    print("--- request as received ---", flush=True)
    print(request.strip())
    print("--- end ---", flush=True)

    key = ""
    for line in request.split("\r\n"):
        if line.lower().startswith("sec-websocket-key:"):
            key = line.split(":", 1)[1].strip()

    accept = expected_accept(key) if key else ""
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n"
        "\r\n"
    )
    print(f"--- server computed accept: {accept} ---", flush=True)
    connection.sendall(response.encode())

    # One server-initiated text frame, unmasked, as a server must send.
    connection.sendall(b"\x81\x05hello")

    try:
        incoming = connection.recv(4096)
    except OSError:
        incoming = b""
    if incoming:
        print(f"--- frame from client: {incoming.hex(' ')} ---", flush=True)
        length = incoming[1] & 0x7F
        mask = incoming[2:6]
        masked_payload = incoming[6 : 6 + length]
        unmasked = bytes(b ^ mask[i % 4] for i, b in enumerate(masked_payload))
        print(f"--- unmasked payload: {unmasked!r} ---", flush=True)
    connection.close()


def serve() -> None:
    print(f"raw WebSocket server on 127.0.0.1:{PORT}", flush=True)
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", PORT))
    listener.listen(5)
    while True:
        connection, address = listener.accept()
        threading.Thread(target=handle, args=(connection, address), daemon=True).start()


# --- the raw client ------------------------------------------------------


def client() -> None:
    import time

    connection = socket.create_connection(("127.0.0.1", PORT))
    request = (
        "GET /chat HTTP/1.1\r\n"
        "Host: 127.0.0.1:8014\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    connection.sendall(request.encode())

    data = b""
    while b"\r\n\r\n" not in data:
        chunk = connection.recv(4096)
        if not chunk:
            break
        data += chunk

    # One recv can return the response headers and the first frame in the same
    # read. Decoding the whole buffer as text dies on the frame's 0x81 byte, so
    # split at the header terminator and keep whatever followed it.
    head, _, leftover = data.partition(b"\r\n\r\n")
    print("--- response ---")
    print(head.decode().strip())
    print("--- end ---")

    frame = leftover if leftover else connection.recv(4096)
    print(f"server frame bytes: {frame.hex(' ')}")
    if frame:
        length = frame[1] & 0x7F
        print(f"opcode 0x{frame[0]:02x}, length {length}, payload {frame[2 : 2 + length]!r}")

    # Client frames must be masked. Any key will do.
    payload = b"hi"
    mask = b"\x01\x02\x03\x04"
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    connection.sendall(bytes([0x81, 0x80 | len(payload)]) + mask + masked)
    time.sleep(0.3)
    connection.close()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "key":
        show_key()
    elif mode == "frame":
        show_frame()
    elif mode == "serve":
        serve()
    elif mode == "client":
        client()
    elif mode == "all":
        show_key()
        show_frame()
    else:
        print(f"unknown mode: {mode}")
        print("try one of: key, frame, serve, client, all")
        sys.exit(1)


if __name__ == "__main__":
    main()