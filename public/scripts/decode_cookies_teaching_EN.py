#!/usr/bin/env python3
"""
Packed Light - cookie decoder (teaching version)

This is a template, not the answer. I left the important
values blank on purpose. If you work through the hints you'll
end up with the same script, but you'll actually know what
it does. If you just fill in the blanks from a writeup, you
learned nothing.

The chain, as seen in the capture:
    keystroke -> XOR(key) -> base64 -> Cookie: hotel_sess_state=<b64>

So each HTTP request carries exactly one encrypted character.
To get it back: base64 decode, then XOR with the key.

HINT 1 - the key
    The server handed out a Python script at /temp/updates.py.
    Follow the HTTP stream in Wireshark and read it.
    There's a getkey() function that builds a string from two
    parts. The key is those two parts glued together.

HINT 2 - the data
    In Wireshark, filter by http.cookie and export the requests
    as plain text (Export -> Packet Dissections -> As Plain Text).
    Every request has:
        Cookie: hotel_sess_state=XXXX
    One cookie, one character. Count the requests: that's how
    long the message is.

HINT 3 - the order
    Each packet has a frame number. Sort them ascending and
    glue the characters in that order.
"""

import base64
import re

# STEP 1 - the key
# Go read the keylogger script (HINT 1). The values live there.
p1 = "???"          # first half of the key
p2 = "???"          # second half
key = (p1 + p2).encode("utf-8")

# STEP 2 - your Wireshark export
PCAP_EXPORT = "/path/to/your/export.txt"   # see HINT 2

with open(PCAP_EXPORT, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# STEP 3 - pull out (frame number, cookie value) pairs
# Matches the "Frame 391: ..." blocks from the Wireshark export (HINT 2).
pattern = re.compile(r"Frame (\d+):.*?hotel_sess_state=([A-Za-z0-9+/=]+)", re.DOTALL)
pairs = pattern.findall(content)
print(f"[*] Extracted {len(pairs)} cookies")

# STEP 4 - sort by frame number (HINT 3)
pairs.sort(key=lambda x: int(x[0]))

# STEP 5 - decode
flag_chars = []
for frame, b64 in pairs:
    raw = base64.b64decode(b64)                                     # strip base64
    plain = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)) # strip XOR
    flag_chars.append(plain.decode("utf-8", errors="replace"))

flag = "".join(flag_chars)
print("[*] Reassembled message:")
print(flag)

