#!/usr/bin/env python3
"""S151 - contexto de un sitio: ventana de codigo -> cadenas referenciadas (regla estricta).

Uso:  .venv/bin/python analysis/s151_panda/ctx.py 0x43793efe [ventana]
"""
import bisect
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096


def cstr(o, maxlen=140):
    e = o
    while e < len(B) and e < o + maxlen and (32 <= B[e] < 127 or B[e] in (9, 10)):
        e += 1
    return B[o:e].decode("latin-1")


def string_refs(lo, hi):
    """[(add_addr, destino, texto)] con la regla estricta (ldr mas cercano del mismo registro)."""
    ldrs = []
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
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                ldrs.append((a, reg, lit, U32(B, o2)[0]))
    by = {}
    for a, reg, lit, w in ldrs:
        by.setdefault(reg, []).append((a, lit, w))
    for v in by.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by.items()}
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        h = U16(B, o)[0]
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by.get(reg, [])
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, lit, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + a + 4) & 0xFFFFFFFF
        if BASE <= tgt < BASE + N:
            t = cstr(tgt - BASE)
            if t and len(t) > 1 and all(32 <= ord(c) < 127 or c in "\n\t" for c in t):
                out.append((a, tgt, t))
    return out


def main():
    addr = int(sys.argv[1], 0)
    win = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x200
    lo = max(BASE, addr - win)
    hi = min(BASE + N, addr + win)
    for a, tgt, t in string_refs(lo, hi):
        print(f"0x{a:08x} -> 0x{tgt:08x}  {t[:120]!r}")


if __name__ == "__main__":
    main()
