#!/usr/bin/env python3
"""S148 — resuelve TODOS los pares PIC (`ldr rX,[pc,#imm]` + `add rX,pc`) de un rango
y muestra el destino (cadena, tabla o dato) de cada `add`.

Uso:  .venv/bin/python analysis/s148_depth/resolve_range.py 0x43562000 0x43562c00
"""
import bisect
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096


def cstr(off, maxlen=90):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def all_ldrs():
    out = []
    for a in range(BASE, BASE + len(B) - 8, 2):
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
            if 0 <= o2 <= len(B) - 4:
                out.append((a, reg, lit, U32(B, o2)[0]))
    return out


def main():
    lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
    ldrs = all_ldrs()
    by_reg = {}
    for a, reg, lit, w in ldrs:
        by_reg.setdefault(reg, []).append((a, lit, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    for a in range(lo, hi, 2):
        o = a - BASE
        h = U16(B, o)[0]
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg, [])
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, lit, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + a + 4) & 0xFFFFFFFF
        s = cstr(tgt - BASE) if BASE <= tgt < BASE + len(B) else ""
        print(f"add 0x{a:08x} (r{reg})  ldr 0x{la:08x}  pool 0x{lit:08x}=0x{w:08x}  -> 0x{tgt:08x}  {s!r}")


if __name__ == "__main__":
    main()
