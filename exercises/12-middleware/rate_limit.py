"""Lesson 12 — rate limiting, and the leak in the obvious implementation.

    python rate_limit.py baseline   # nothing stops you
    python rate_limit.py fixed      # fixed window counter, and its boundary leak
    python rate_limit.py sliding    # sliding window log
    python rate_limit.py bucket     # token bucket
    python rate_limit.py headers    # what the client is told when it is refused
    python rate_limit.py all

The subject under test is one function:

    allow(key, now) -> (allowed: bool, info: dict)

`now` is passed in rather than read from the clock, so every case here is
reproducible and finishes immediately. A real limiter would use time.time().
"""

import sys
from collections import deque

LIMIT = 5
WINDOW = 60  # seconds


class Decision:
    def __init__(self, allowed: bool, info: dict) -> None:
        self.allowed = allowed
        self.info = info


# --- 1. No limiter at all -------------------------------------------------


def allow_nothing(key: str, now: float) -> Decision:
    """Every request passes. This is what the app looked like before."""
    return Decision(True, {})


# --- 2. Fixed window ------------------------------------------------------


class FixedWindow:
    """Count requests per key per calendar window.

    This is what most people write, and it is broken at the boundary.
    """

    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        self.counts: dict[str, tuple[int, int]] = {}

    def allow(self, key: str, now: float) -> Decision:
        slot = int(now // self.window)
        count, seen_slot = self.counts.get(key, (0, slot))
        if slot != seen_slot:
            count, seen_slot = 0, slot
        if count >= self.limit:
            retry_after = self.window - (now % self.window)
            return Decision(False, {"retry_after": int(retry_after) + 1})
        self.counts[key] = (count + 1, slot)
        return Decision(True, {"used": count + 1, "limit": self.limit})


# --- 3. Sliding window log ------------------------------------------------


class SlidingWindow:
    """Keep the timestamp of every request and drop the ones that aged out.

    Exact, and the cost is memory proportional to what you allow.
    """

    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        self.logs: dict[str, deque] = {}

    def allow(self, key: str, now: float) -> Decision:
        log = self.logs.setdefault(key, deque())
        while log and now - log[0] >= self.window:
            log.popleft()
        if len(log) >= self.limit:
            return Decision(False, {"retry_after": int(log[0] + self.window - now) + 1})
        log.append(now)
        return Decision(True, {"used": len(log), "limit": self.limit})


# --- 4. Token bucket ------------------------------------------------------


class TokenBucket:
    """Allow a burst, then refill at a steady rate.

    limit is the bucket size (the biggest burst), refill is tokens per second.
    """

    def __init__(self, burst: int, refill_per_second: float) -> None:
        self.burst = burst
        self.refill = refill_per_second
        self.buckets: dict[str, tuple[float, float]] = {}

    def allow(self, key: str, now: float) -> Decision:
        tokens, seen = self.buckets.get(key, (float(self.burst), now))
        tokens = min(self.burst, tokens + (now - seen) * self.refill)
        if tokens < 1:
            return Decision(False, {"retry_after": int((1 - tokens) / self.refill) + 1})
        self.buckets[key] = (tokens - 1, now)
        return Decision(True, {"tokens_left": round(tokens - 1, 2)})


# --- The cases ------------------------------------------------------------


def report(name: str, limiter, key: str, times: list[float]) -> None:
    granted = 0
    first_refusal = None
    for now in times:
        decision = limiter.allow(key, now) if hasattr(limiter, "allow") else limiter(key, now)
        if decision.allowed:
            granted += 1
        elif first_refusal is None:
            first_refusal = decision.info
    print(f"  {name}")
    print(f"    sent {len(times)}, allowed {granted}")
    if first_refusal:
        print(f"    first refusal: {first_refusal}")


def run_baseline() -> None:
    print("1. No limiter")
    report("60 requests in 60 seconds", allow_nothing, "iris", [n for n in range(60)])
    print("   nothing counted, nothing refused, nothing logged")


def run_fixed() -> None:
    print(f"2. Fixed window: {LIMIT} per {WINDOW}s")
    report(
        "all inside one window, 1s apart",
        FixedWindow(LIMIT, WINDOW),
        "iris",
        [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    )

    print(f"   now the same client, {LIMIT} requests at the end of one window...")
    report(
        f"5 at t=56..59, then 5 at t=60..63",
        FixedWindow(LIMIT, WINDOW),
        "iris",
        [56.0, 57.0, 58.0, 59.0, 59.5, 60.0, 61.0, 62.0, 63.0, 64.0],
    )
    print(f"   10 requests in 9 seconds, limit is {LIMIT}.")
    print("   The counter went back to zero at t=60, so the second batch never felt it.")


def run_sliding() -> None:
    print("3. Sliding window log, same 10 requests")
    report(
        "5 at t=56..59, then 5 at t=60..63",
        SlidingWindow(LIMIT, WINDOW),
        "iris",
        [56.0, 57.0, 58.0, 59.0, 59.5, 60.0, 61.0, 62.0, 63.0, 64.0],
    )
    limiter = SlidingWindow(LIMIT, WINDOW)
    for now in [56.0, 57.0, 58.0, 59.0, 59.5, 60.0]:
        limiter.allow("iris", now)
    print(f"   timestamps kept for one key: {len(limiter.logs['iris'])}")
    print("   memory grows with what you allow, which is the price of exactness")


def run_bucket() -> None:
    print("4. Token bucket: burst of 3, refilling 1 per second")
    report(
        "4 at t=0, then 1 per second",
        TokenBucket(burst=3, refill_per_second=1),
        "iris",
        [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0],
    )
    print("   3 got through at t=0, the 4th was refused, then 1 per second")
    print("   this is the shape you want for an API: short bursts pass, sustained load does not")


def run_headers() -> None:
    print("5. What the client is told when it is refused")
    limiter = FixedWindow(LIMIT, WINDOW)
    for _ in range(LIMIT):
        limiter.allow("iris", 10.0)
    decision = limiter.allow("iris", 11.0)
    print(f"   the limiter says: allowed={decision.allowed}, retry after {decision.info['retry_after']}s")
    print()
    print("   and the response the client actually receives:")
    print("   HTTP/1.1 429 Too Many Requests")
    print(f"   Retry-After: {decision.info['retry_after']}")
    print('   content-type: application/json')
    print('   {"detail":"Rate limit exceeded"}')
    print()
    print("   the three codes are not interchangeable:")
    print("     401  you have not proved who you are      -> log in")
    print("     403  you are known, and you may not do it -> stop asking")
    print("     429  you are fine, but not this often      -> slow down")
    print("   RFC 6585 added 429 for the third one. It is not a 403 and not a 503.")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "baseline": run_baseline,
        "fixed": run_fixed,
        "sliding": run_sliding,
        "bucket": run_bucket,
        "headers": run_headers,
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