#!/usr/bin/env python3
"""Volcado de cadenas ASCII de un rango de offsets de fichero de un ELF."""
import sys

fn, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
d = open(fn, "rb").read()[a:b]
cur = []
start = 0
for i, ch in enumerate(d):
    if 32 <= ch < 127:
        if not cur:
            start = i
        cur.append(chr(ch))
    else:
        if len(cur) >= 6:
            print("%#010x %s" % (a + start, "".join(cur)))
        cur = []
if len(cur) >= 6:
    print("%#010x %s" % (a + start, "".join(cur)))
