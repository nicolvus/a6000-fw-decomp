#!/usr/bin/env python3
"""S148 — utilidades: mapa global PIC -> funcion, y volcado de cadenas de una banda.

Uso:
  .venv/bin/python analysis/s148_depth/refs.py 0x43c24b46 0x43c24b85 ...
  .venv/bin/python analysis/s148_depth/refs.py --band 0x43562000 0x43562a00
"""
import bisect
import json
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
GLOBAL = os.path.join(REPO, "analysis/s106_imaging_cap/pic_refs_strict_global.json")
B = open(BIN, "rb").read()
U16 = struct.Struct("<H").unpack_from


def cstr(off, maxlen=200):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def prologues():
    out = []
    for a in range(BASE, BASE + len(B) - 4, 2):
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16(B, o + 2)[0] & 0x4000):
            out.append(a)
    return out


def main():
    gmap = {int(k, 16): v for k, v in json.load(open(GLOBAL)).items()}
    starts = prologues()
    if sys.argv[1] == "--band":
        lo, hi = int(sys.argv[2], 0), int(sys.argv[3], 0)
        # todas las cadenas referenciadas por un `add` dentro de la banda
        hits = []
        for dest, sites in gmap.items():
            for s in sites:
                if lo <= s < hi:
                    i = bisect.bisect_right(starts, s) - 1
                    f = starts[i] if i >= 0 else 0
                    hits.append((s, f, dest, cstr(dest - BASE)))
        for s, f, dest, t in sorted(hits):
            print(f"0x{s:08x} func=0x{f:08x}  0x{dest:08x} {t!r}")
        return

    for arg in sys.argv[1:]:
        a = int(arg, 0)
        sites = sorted(set(gmap.get(a, [])))
        print(f"=== 0x{a:08x} {cstr(a - BASE)!r}")
        # punteros absolutos
        pat = struct.pack("<I", a)
        idx = 0
        abs_p = []
        while True:
            i = B.find(pat, idx)
            if i < 0:
                break
            abs_p.append(BASE + i)
            idx = i + 1
        if abs_p:
            print(f"    punteros absolutos: {[hex(x) for x in abs_p]}")
        for s in sites:
            i = bisect.bisect_right(starts, s) - 1
            f = starts[i] if i >= 0 else 0
            print(f"    PIC 0x{s:08x}  func=0x{f:08x}")
        if not sites and not abs_p:
            print("    SIN REFERENCIA (PIC ni absoluta)")


if __name__ == "__main__":
    main()
