#!/usr/bin/env python3
"""S170 — delimita funciones del módulo [ILLUMI] y lista TODAS las cadenas
referenciadas en su zona de código (incluye __PRETTY_FUNCTION__ y ficheros fuente).

Zona de código del módulo: 0x435ab000 .. 0x435af000 (derivada de los 52 sitios PIC).
"""
import bisect
import json
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

LO, HI = 0x435ab000, 0x435af000


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


def string_starts(lo, hi):
    out = set()
    prev = False
    for i in range(max(0, lo - BASE), min(N, hi - BASE)):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


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


def strict_pairs(lo, hi):
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
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
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        out.append((a, la, lit, w, reg, (w + (a + 4)) & 0xFFFFFFFF))
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
    starts = string_starts(0, 0xFFFFFFFF)
    pairs = strict_pairs(LO, HI)
    strrefs = {}
    for a, la, lit, w, reg, dest in pairs:
        if dest in starts:
            strrefs.setdefault(dest, []).append(a)

    fs = func_starts(LO, HI)
    # deduplica y ordena
    fs = sorted(set(fs))
    fskeys = fs

    def enclosing(addr):
        i = bisect.bisect_right(fskeys, addr) - 1
        if i < 0:
            return None, None
        s = fskeys[i]
        # fin = siguiente prólogo
        j = bisect.bisect_right(fskeys, addr)
        e = fskeys[j] if j < len(fskeys) else None
        return s, e

    rows = []
    for dest, sites in sorted(strrefs.items()):
        for s in sites:
            fs_, fe_ = enclosing(s)
            rows.append({"sitio": hex(s), "cadena_addr": hex(dest),
                         "texto": cstr(dest), "func_start": hex(fs_) if fs_ else None,
                         "func_end_guess": hex(fe_) if fe_ else None})
    json.dump(rows, open("analysis/s170_illumi/illumi_region_strings.json", "w"), indent=1)

    # agrupa por función
    byfunc = {}
    for r in rows:
        byfunc.setdefault(r["func_start"], []).append(r)
    print(f"cadenas referenciadas en la zona: {len(strrefs)}  sitios: {len(rows)}  funciones: {len(byfunc)}")
    print()
    for f in sorted(byfunc, key=lambda x: int(x, 16) if x else 0):
        print(f, len(byfunc[f]))
        for r in sorted(byfunc[f], key=lambda x: int(x["sitio"], 16)):
            print("   ", r["sitio"], hex(int(r["cadena_addr"], 16)), repr(r["texto"])[:95])
    print()
    print("prologos en la zona:", len(fs))


if __name__ == "__main__":
    main()
