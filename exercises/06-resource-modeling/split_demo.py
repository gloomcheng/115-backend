"""Lesson 06 — what splitting one program into two actually costs.

    python split_demo.py inprocess   # two modules, one process, direct call
    python split_demo.py overhttp    # two processes, HTTP between them
    python split_demo.py both        # both paths, and the ratio between them
    python split_demo.py trigger     # when to split, and when not to
    python split_demo.py all

Both halves compute the same thing and return the same answers. Only the
failure model changes, and that is the entire lesson.
"""

import http.client
import json
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT_A = 8031  # the "users" service
PORT_B = 8032  # the "orders" service

ORDERS = 1000
CALLS = 300


# --- the two pieces of business logic -------------------------------------


def total_for_user(user_id: int) -> dict:
    """What the orders service knows. Pure, fast, cannot hang."""
    return {"user_id": user_id, "orders": user_id * 7, "total": user_id * 7 * 250}


def user_total_inprocess(user_id: int) -> dict:
    """Call the other piece of logic directly. Same process."""
    return total_for_user(user_id)


def user_total_overhttp(user_id: int) -> dict:
    """Call the other piece over HTTP. Same answer, different failure modes."""
    connection = http.client.HTTPConnection("127.0.0.1", PORT_B, timeout=5)
    connection.request("GET", f"/totals/{user_id}")
    response = connection.getresponse()
    payload = json.loads(response.read())
    connection.close()
    if response.status != 200:
        raise RuntimeError(f"orders service said {response.status}")
    return payload


# --- the second process ---------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def do_GET(self):
        parts = self.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "totals":
            body = json.dumps(total_for_user(int(parts[1]))).encode()
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # A deliberately slow route, used to show what a timeout is for.
        if len(parts) == 2 and parts[0] == "slow-totals":
            time.sleep(10)
            body = b'{"detail":"finished after nobody is listening"}'
            self.send_response(200)
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404)


def bench(callable_, label: str) -> float:
    # perf_counter_ns, because a direct function call finishes in a fraction
    # of a microsecond and prints as 0.00 ms at millisecond resolution, which
    # is the same as printing nothing.
    start = time.perf_counter_ns()
    for user_id in range(1, CALLS + 1):
        callable_(user_id)
    elapsed_ns = time.perf_counter_ns() - start
    elapsed = elapsed_ns / 1_000_000
    print(f"   {label}")
    print(f"     {CALLS} calls in {elapsed:.1f} ms")
    print(f"     {elapsed_ns / CALLS:,.0f} ns per call")
    return elapsed_ns / CALLS


def run_both() -> None:
    """Run the two paths and print the ratio, so the multiplier has a source.

    The lesson argues from the ratio. If the ratio only exists in prose, it
    drifts the moment either timing moves, which both of them do.
    """
    direct_ns = bench(total_for_user, "in-process function call")
    server = ThreadingHTTPServer(("127.0.0.1", PORT_B), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        over_ns = bench(user_total_overhttp, "HTTP call to the other process")
    finally:
        server.shutdown()

    print()
    print(f"   ratio: {over_ns / direct_ns:,.0f}x more expensive per call")
    print()
    print("   Do not quote that ratio. Across six runs with pauses it moved")
    print("   between about 1,500x and about 7,900x, because the HTTP side")
    print("   carries whatever else this machine is doing. What holds every")
    print("   time is the order of magnitude: hundreds of nanoseconds against")
    print("   hundreds of microseconds. Three orders, at least a thousandfold.")


def run_inprocess() -> None:
    print("1. Two modules, one process")
    print()
    print("   orders logic lives in a function. users calls it directly.")
    print()
    bench(user_total_inprocess, "direct function call")
    print()
    print("   a slow query here would make the whole program slow, and it would")
    print("   be obvious: one process, one stack trace, one restart.")
    print()
    print("   And this is the important part: the call cannot fail on its own.")
    print("   It either returns an answer or raises, and you are still standing")
    print("   right there.")


def run_overhttp() -> None:
    print("2. The same logic, in a second process")
    print()
    server = ThreadingHTTPServer(("127.0.0.1", PORT_B), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(0.3)
    try:
        bench(user_total_overhttp, "HTTP call to the other process")
        first = user_total_overhttp(3)
        direct = total_for_user(3)
        print()
        print(f"   over http : {first}")
        print(f"   direct    : {direct}")
        print(f"   identical : {first == direct}")

        print()
        print("   Now make that other process too slow to answer.")
        start = time.perf_counter()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", PORT_B, timeout=1)
            connection.request("GET", "/slow-totals/1")
            connection.getresponse().read()
            outcome = "answered"
        except TimeoutError:
            outcome = "client gave up after 1s"
        except OSError:
            outcome = "connection failed"
        elapsed = time.perf_counter() - start
        print(f"   outcome   : {outcome} ({elapsed:.1f}s)")
        print()
        print("   This is the new thing. In process one, a slow callee could not")
        print("   be abandoned. Across a network it can, and now the caller has a")
        print("   failure mode that did not exist before the split: the other side")
        print("   being alive but not answering.")
    finally:
        server.shutdown()


def run_trigger() -> None:
    print("3. When to split, and when not to")
    print()
    print("   The reason is NOT that the file is long. Long files are annoying,")
    print("   not expensive.")
    print()
    print("   Split when one thing has to change for two different reasons:")
    print()
    print("     - two teams own it and they ship on different days")
    print("     - one part needs to scale up and the rest must not")
    print("     - one part has a different availability requirement, so one")
    print("       deploy must not be able to take the other one down")
    print()
    print("   Do not split because:")
    print()
    print("     - the file is long        -> move it to another file, same process")
    print("     - there is shared state   -> that is the thing splitting makes worse")
    print("     - it feels more scalable  -> it is, eventually, after a lot of work")
    print()
    print("   A first project should almost never be split. The honest cost is")
    print("   in the previous section: every direct call becomes a call that can")
    print("   time out, and a call that times out has to be retried, and a retry")
    print("   that repeats a side effect has to be idempotent. Unit 03 sections 07")
    print("   and 08 are the two halves of that bill.")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "inprocess": run_inprocess,
        "overhttp": run_overhttp,
        "both": run_both,
        "trigger": run_trigger,
    }
    if mode == "all":
        for runner in runners.values():
            runner()
    elif mode in runners:
        runners[mode]()
    else:
        print(f"unknown mode: {mode}")
        print(f"try one of: {', '.join(runners)}")
        sys.exit(1)


if __name__ == "__main__":
    main()