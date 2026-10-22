#!/usr/bin/env python3
"""S180 - volcar un pool de literales con resolucion a cadenas (A6000)."""
import struct, sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    if e == o:
        return None
    return B[o:e].decode("latin1")


lo = int(sys.argv[1], 0)
hi = int(sys.argv[2], 0)
for a in range(lo, hi, 4):
    v = struct.unpack_from("<I", B, a - BASE)[0]
    s = cstr(v)
    print(f"0x{a:08x}  0x{v:08x}  {('-> ' + repr(s)) if s else ''}")
