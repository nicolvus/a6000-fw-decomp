#!/usr/bin/env python3
"""Cliente del demonio. q.py SOCK guion.json SALIDA.jsonl | q.py SOCK --shutdown"""
import sys, socket, json
s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1])
req = {"shutdown": True} if sys.argv[2] == "--shutdown" else {"calls": json.load(open(sys.argv[2]))}
s.sendall((json.dumps(req) + "\n").encode())
f = s.makefile("rb"); out = open(sys.argv[3], "ab") if len(sys.argv) > 3 else sys.stdout.buffer
for l in f: out.write(l)
