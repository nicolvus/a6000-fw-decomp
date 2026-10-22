#!/usr/bin/env python3
"""S138 — lista las cadenas referenciadas por el código en un rango (mapa global PIC)."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")

B = open(BIN, "rb").read()


def cstr(off):
    e = B.find(b"\x00", off)
    return B[off:e].decode("latin1")


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    g = json.load(open(GLOBAL))
    rows = []
    for dest, sites in g.items():
        dv = int(dest, 16)
        hit = [s for s in sites if lo <= s < hi]
        if not hit:
            continue
        off = dv - BASE
        if off < 0 or off >= len(B):
            continue
        rows.append((min(hit), dv, cstr(off), hit))
    rows.sort()
    for first, dv, txt, hit in rows:
        print(f"0x{dv:08x}  n={len(hit):3d}  {txt[:140]!r}")
        if len(sys.argv) > 3 and sys.argv[3] == "-v":
            for s in hit:
                print(f"        0x{s:x}")


if __name__ == "__main__":
    main()
