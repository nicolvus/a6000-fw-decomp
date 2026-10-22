#!/usr/bin/env python3
"""S169 — vuelca el mapa global de referencias PIC (regla estricta) de un blob arbitrario.

Réplica de `analysis/s106_imaging_cap/scan_pic_refs_strict.py` con *blob* y *base* como
parámetros, para poder hacerlo sobre la A7S fw3.20 y el A6300 fw2.01 (el mapa de la A6000
ya existe en `analysis/s106_imaging_cap/pic_refs_strict_global.json`).

Salida: JSON `{destino_hex: [sitios_hex]}`.

Uso: scan_all_refs.py <blob> <base> <salida.json>
"""
import bisect
import json
import struct
import sys

blob = sys.argv[1]
BASE = int(sys.argv[2], 16)
OUT = sys.argv[3]
B = open(blob, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096


def string_starts():
    out = set()
    prev = False
    for i in range(N):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites():
    out = []
    a = BASE
    while a < BASE + N:
        o = a - BASE
        if o < 0 or o > N - 4:
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
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                out.append((a, reg, U32(B, o2)[0]))
        a += 2
    return out


def add_sites():
    out = []
    a = BASE
    while a < BASE + N:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def scan():
    starts = string_starts()
    by_reg = {}
    for a, reg, w in ldr_sites():
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in add_sites():
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_left(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return out


res = scan()
with open(OUT, "w") as fh:
    json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())}, fh, indent=0)
print(f"destinos: {len(res)}  ->  {OUT}")
