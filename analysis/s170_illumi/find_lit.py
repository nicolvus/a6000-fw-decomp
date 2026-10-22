#!/usr/bin/env python3
"""S170 — para un valor literal dado, lista los sitios `add rX,pc` cuyo pool lo contiene
(regla PIC estricta) y las funciones que los contienen.

Uso:  find_lit.py 0x7a0020
"""
import bisect
import json
import struct
import sys

BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
LO, HI = 0x43541000, 0x44017000


def ldr_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def func_starts(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x0100) and (h & 0x00FF):
            out.append(a)
        elif h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def main():
    target = int(sys.argv[1], 0)
    ldrs = ldr_sites(LO, HI)
    adds = add_sites(LO, HI)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    fs = sorted(set(func_starts(LO, HI)))

    hits = []
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        if w == target:
            dest = (w + a + 4) & 0xFFFFFFFF
            j = bisect.bisect_right(fs, a) - 1
            hits.append({"sitio": hex(a), "ldr": hex(la), "pool": hex(lit),
                         "dest": hex(dest), "func": hex(fs[j]) if j >= 0 else None})
    for h in hits:
        print(h)
    print(f"total {len(hits)}")


if __name__ == "__main__":
    main()
