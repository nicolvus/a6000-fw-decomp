#!/usr/bin/env python3
"""S144 — para cada sitio de llamada, identifica la funcion que lo contiene y
el modulo (prefijo de traza) mas cercano por codigo.

Uso:  .venv/bin/python analysis/s144_cam_util_sens/ctx.py 0x4376bf92 0x43783136 ...
"""
import bisect
import json
import os
import re
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096


def cstr(off, maxlen=160):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def build():
    ldrs = []
    adds = []
    for a in range(BASE, BASE + N - 8, 2):
        o = a - BASE
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                ldrs.append((a, reg, U32(B, o2)[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    pic = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        pic.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    return pic


def prologues():
    out = []
    for a in range(BASE, BASE + N - 4, 2):
        o = a - BASE
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16(B, o + 2)[0] & 0x4000):
            out.append(a)
    return out


if __name__ == "__main__":
    pic = build()
    starts = prologues()
    for s in sys.argv[1:]:
        site = int(s, 0)
        i = bisect.bisect_right(starts, site) - 1
        f = starts[i] if i >= 0 else 0
        # cadenas referenciadas dentro de la funcion (mismo prefijo)
        mods = []
        for dest, ss in pic.items():
            if not ss:
                continue
            if f <= ss[0] < (starts[i + 1] if i + 1 < len(starts) else f + 0x4000):
                mods.append((ss[0], cstr(dest - BASE)))
        mods.sort()
        pref = {}
        for sa, t in mods:
            m = re.match(r"\[([A-Z0-9_]+)\]", t)
            if m:
                pref.setdefault(m.group(1), []).append((sa, t))
        best = sorted(pref.items(), key=lambda kv: -len(kv[1]))[:3]
        print(f"sitio 0x{site:08x} -> funcion 0x{f:08x}")
        for k, v in best:
            print(f"    modulo [{k}]  ({len(v)} cadenas)")
            for sa, t in v[:3]:
                print(f"        0x{sa:08x} {t[:90]}")
