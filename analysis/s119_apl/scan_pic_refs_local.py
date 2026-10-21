#!/usr/bin/env python3
"""S119 — escáner PIC reducido (destinos en la zona de datos 0x43c90000-0x43d00000).

Es el mismo esquema que `analysis/s106_imaging_cap/scan_pic_refs.py` (regla canónica del
repo: todos los `ldr` del registro dentro de 4 KB, aceptando sólo destinos que caen en
el inicio de una cadena), pero limitado a la zona de datos útil para este hito, de modo
que el JSON resultante sea manejable.

Uso: python3 scan_pic_refs_local.py
Salida: analysis/s119_apl/pic_refs.json
"""
import bisect
import json
import os
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
STR_LO, STR_HI = 0x43C90000, 0x43D00000
MAX_LDR_GAP = 4096

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def string_starts(lo, hi):
    out = set()
    prev = False
    for i in range(lo - BASE, hi - BASE):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, U32(B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def main():
    starts = string_starts(STR_LO, STR_HI)
    ldrs = ldr_sites(BASE, BASE + N)
    adds = add_sites(BASE, BASE + N)
    by_reg = defaultdict(list)
    for a, reg, w in ldrs:
        by_reg[reg].append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = defaultdict(list)
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        while i >= 0:
            la, w = v[i]
            if a - la > MAX_LDR_GAP:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt in starts:
                out[tgt].append(a)
            i -= 1
    res = {f"0x{k:x}": sorted(set(v)) for k, v in sorted(out.items())}
    json.dump(res, open(os.path.join(HERE, "pic_refs.json"), "w"), indent=0)
    print(f"destinos: {len(res)}  (rango de cadenas {STR_LO:#x}-{STR_HI:#x})")


if __name__ == "__main__":
    main()
