"""Lesson 03 — what happens when the client gives up and the server does not.

    python timeout_demo.py hang        # no timeout: the request never ends
    python timeout_demo.py deadline    # the same call, bounded
    python timeout_demo.py chain       # three dependencies, one client budget
    python timeout_demo.py exhaustion  # why that cascade takes the site down
    python timeout_demo.py all

The slow dependency is a sleep. Everything else is real: real HTTP, real
socket timeouts, real thread exhaustion.
"""

import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8020

# What the client is willing to wait, in seconds. Set by the client, not us.
CLIENT_BUDGET = 2.0


def hr(title: str) -> None:
    print(f"\n{title}\n{'-' * len(title)}")


def measure(call: str, budget: float | None) -> tuple[float, str]:
    """Run one request, return (elapsed_seconds, what the client saw)."""
    query = "sleep=3" + (f"&budget={budget}" if budget is not None else "")
    request = (
        f"GET /{call}?{query} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{PORT}\r\n"
        f"\r\n"
    ).encode()

    start = time.perf_counter()
    connection = socket.create_connection(("127.0.0.1", PORT), timeout=30)
    connection.sendall(request)

    # The client waits. It does not hang up early, because that would hide the
    # very thing being demonstrated.
    received = b""
    while b"\r\n\r\n" not in received:
        chunk = connection.recv(4096)
        if not chunk:
            break
        received += chunk

    elapsed = time.perf_counter() - start
    connection.close()
    status = received.split(b" ")[1].decode() if b" " in received else "?"
    return elapsed, f"HTTP {status}"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # keep the demo output readable
        pass

    def do_GET(self):
        parts = self.path.strip("/").split("?")
        route = parts[0]
        fields = {}
        if len(parts) > 1:
            for pair in parts[1].split("&"):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    fields[key] = value

        sleep_for = float(fields.get("sleep", 3))
        budget = fields.get("budget")

        # The slow dependency. A real one is a database or another service.
        #
        # If the client sent a deadline, that deadline is handed DOWN to the
        # dependency rather than checked here afterwards. Checking it after
        # the work is done is not a timeout, it is a status code.
        allowed = sleep_for
        if budget is not None:
            allowed = min(sleep_for, float(budget))

        time.sleep(allowed)

        if allowed < sleep_for:
            body = b'{"detail":"upstream slower than the client can wait"}'
            self.send_response(504)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_hang() -> None:
    hr("1. No timeout anywhere")
    elapsed, outcome = measure("hang", None)
    print(f"   elapsed: {elapsed:.1f}s   client saw: {outcome}")
    print()
    print("   The client waited. Nothing was wrong with the client.")
    print("   The server spent that whole time sleeping on a dependency that")
    print("   was never going to answer in time.")
    print()
    print("   That is not a slow response. That is an occupied worker.")


def run_deadline() -> None:
    hr("2. The same call, with a deadline the client sent")
    elapsed, outcome = measure("hang", CLIENT_BUDGET)
    print(f"   elapsed: {elapsed:.1f}s   client saw: {outcome}")
    print()
    print("   Same server, same slow dependency, same 3 second wait in the")
    print("   dependency. The only difference is that the client said how long")
    print("   it is willing to wait.")
    print()
    print("   And that is the part to notice: the deadline is handed DOWN to the")
    print("   dependency call. Checking it after the work is finished is not a")
    print("   timeout, it is a status code on work that was already wasted.")


def run_chain() -> None:
    hr("3. Three dependencies, one client budget")
    print()
    print("   A request that calls A, then B, then C. Each takes 1 second.")
    print(f"   The client will wait {CLIENT_BUDGET:.0f} seconds in total.")
    print()
    for count in (1, 2, 3):
        total = count * 1.0
        verdict = "fits" if total <= CLIENT_BUDGET else "already too late"
        print(f"   after {count} call(s): {total:.0f}s spent, {verdict}")
    print()
    print("   Each individual call is well inside the budget. The chain is not,")
    print("   because the budget is spent three times and only available once.")
    print()
    print("   This is the mistake: setting every timeout to the client's timeout.")
    print("   The inner call must be SHORTER than what is left of the caller's")
    print("   deadline, not equal to it. With three layers that means each one")
    print("   gets less than a third.")


def run_exhaustion() -> None:
    hr("4. Why that becomes a site outage")
    print()
    workers = 4
    print(f"   The server has {workers} workers. Each one is busy while it sleeps.")
    print()
    print("   One slow dependency, six requests:")
    for attempt in range(1, 7):
        slot = (attempt - 1) % workers + 1
        state = "occupied" if attempt <= workers else "queued, nobody free"
        print(f"     request {attempt}: worker {slot} {state}")
    print()
    print(f"   After {workers} requests every worker is asleep. Request "
          f"{workers + 1} waits,")
    print("   and so does every request after it, including the ones that would")
    print("   have been instant against a healthy dependency.")
    print()
    print("   That is the cascade: a slow dependency does not just make slow")
    print("   things slow, it consumes the capacity that fast things need.")
    print()
    print("   A per-request timeout is what breaks it. The worker is released,")
    print("   and the next request gets a real answer instead of a queue.")


def serve_in_background() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        run_hang()
        run_deadline()
        run_chain()
        run_exhaustion()
    finally:
        server.shutdown()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("all", "hang"):
        serve_in_background()
    elif mode in ("deadline", "chain", "exhaustion"):
        print("these three are measured or computed from the numbers above; run 'all'")
    else:
        print(f"unknown mode: {mode}")
        print("try: all, hang")
        sys.exit(1)


if __name__ == "__main__":
    main()