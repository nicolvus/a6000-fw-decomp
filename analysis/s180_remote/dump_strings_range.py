#!/usr/bin/env python3
"""S180 - volcar todas las cadenas en el rango del bloque [REMOTE] y sus vecinas."""
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()

lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x43c25b00
hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x43c26400
o0, o1 = lo - BASE, hi - BASE
i = o0
prev = False
while i < o1:
    c = B[i]
    if 32 <= c < 127:
        if not prev:
            s = i
            e = i
            while e < len(B) and 32 <= B[e] < 127:
                e += 1
            print(f"0x{s+BASE:08x}  {B[s:e].decode('latin1')!r}")
            i = e
            prev = False
            continue
    prev = 32 <= c < 127
    i += 1
