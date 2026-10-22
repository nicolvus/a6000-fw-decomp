#!/usr/bin/env python3
"""S156 — reconstrucción del módulo [TP_R] (A6000 fw3.21).

Sólo bytes. Sin REA/Ghidra.
"""
import json
import re
import struct
import subprocess
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

PIC = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))


def cstr(addr):
    o = addr - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0:
        return None
    try:
        return B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None


def all_strings():
    """[(addr, texto)] de todas las cadenas imprimibles."""
    out = []
    start = None
    cur = bytearray()
    for i in range(N):
        c = B[i]
        if 32 <= c < 127:
            if start is None:
                start = i
            cur.append(c)
        else:
            if start is not None and len(cur) >= 2:
                out.append((BASE + start, bytes(cur).decode("ascii", "replace")))
            start = None
            cur = bytearray()
    return out


def pic_ldr_sites(lo, hi):
    """[(addr, reg, valor_literal, dir_literal)] de `ldr rX,[pc,#imm]`."""
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


def pic_add_sites(lo, hi):
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


def strict_sites(lo, hi):
    """Regla canónica: cada `add rX,pc` con el `ldr rX,[pc,#imm]` más cercano."""
    import bisect
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = []
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        out.append((a, tgt, la))
    return out


def func_start(addr):
    """Prólogo Thumb más cercano hacia atrás (heurística S151)."""
    o = addr - BASE
    a = o - (o % 2)
    while a >= max(0, o - 0x4000):
        h1 = U16(B, a)[0]
        hit = False
        if (h1 & 0xFE00) == 0xB400 and (h1 & 0x00FF) != 0:
            hit = True
        elif a + 4 <= N and h1 == 0xE92D:
            hit = True
        if hit:
            return BASE + a
        a -= 2
    return None
