#!/usr/bin/env python3
"""S168 — mapa vivo/muerto de las cadenas de una banda de `.rodata` (blob arbitrario).

Para cada cadena de la banda `[lo, hi)`:
  * nº de referencias PIC (regla estricta, la canónica del repo);
  * si existe algún puntero absoluto de 4 B a su inicio;
  * si existen halves `movw`/`movt` adyacentes que la compongan.

Uso: alive_map.py <blob> <base> <lo> <hi>
Salida: JSON en stdout.
"""
import json
import struct
import sys

blob = sys.argv[1]
BASE = int(sys.argv[2], 16)
LO = int(sys.argv[3], 16)
HI = int(sys.argv[4], 16)
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
        if (h & 0xF800) == 0x4800:              # ldr rT,[pc,#imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:            # ldr.w rT,[pc,#imm12]
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


def cstr(va):
    o = va - BASE
    e = B.find(b"\x00", o)
    if e < 0:
        e = o + 120
    return B[o:e].decode("latin1")


def absolute_ptr(va):
    pat = struct.pack("<I", va)
    idx = 0
    out = []
    while True:
        i = B.find(pat, idx)
        if i < 0:
            break
        out.append(BASE + i)
        idx = i + 1
    return out


def movw_movt(va):
    lo, hi = va & 0xFFFF, (va >> 16) & 0xFFFF
    out = []
    idx = 0
    while True:
        i = B.find(struct.pack("<H", lo), idx)
        if i < 0:
            break
        for d in (-4, -2, 2, 4):
            p = i + d
            if 0 <= p <= N - 2 and U16(B, p)[0] == hi:
                out.append(BASE + i)
        idx = i + 1
    return out


import bisect  # noqa: E402  (usado en scan())

refs = scan()
res = []
va = LO
while va < HI:
    o = va - BASE
    if o > 0 and 32 <= B[o - 1] < 127:
        va += 1
        continue
    s = cstr(va)
    if len(s) >= 4:
        res.append({
            "addr": f"{va:08x}",
            "text": s,
            "refs_pic": [f"{x:08x}" for x in sorted(set(refs.get(va, [])))],
            "n_refs_pic": len(set(refs.get(va, []))),
            "punteros_absolutos": [f"{x:08x}" for x in absolute_ptr(va)],
            "movw_movt": [f"{x:08x}" for x in movw_movt(va)],
        })
    va += 1

print(json.dumps({"blob": blob, "base": f"{BASE:08x}", "banda": [f"{LO:08x}", f"{HI:08x}"],
                  "cadenas": res}, indent=1, ensure_ascii=False))
