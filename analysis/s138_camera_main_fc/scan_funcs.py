#!/usr/bin/env python3
"""S138 — límites de función (heurística de prólogo Thumb) y llamadores.

Uso:
  .venv/bin/python analysis/s138_camera_main_fc/scan_funcs.py 0x437b6000 0x437b8400
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()


def prologues(lo, hi):
    """Inicios de función Thumb: `push {...,lr}` (B5xx) o `push.w {...,lr}` (E92D)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (struct.unpack_from("<H", B, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def bl_sites(data, lo, hi):
    out = []
    for a in range(lo, hi - 4, 2):
        o = a - BASE
        h1, h2 = struct.unpack_from("<HH", data, o)
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000:
            s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
            if s & 0x400000:
                s -= 0x800000
            out.append((a, (a + 4 + s) & 0xFFFFFFFF))
    return out


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    ps = prologues(lo, hi)
    print(f"prólogos en 0x{lo:x}-0x{hi:x}: {len(ps)}")
    for p in ps:
        print(f"  0x{p:x}")
    bl = bl_sites(B, lo, hi)
    print(f"bl en el rango: {len(bl)}")
    tgts = sorted(set(t for _, t in bl))
    for t in tgts:
        print(f"  bl -> 0x{t:x}")


if __name__ == "__main__":
    main()
