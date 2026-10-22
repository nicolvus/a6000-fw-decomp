#!/usr/bin/env python3
"""S144 — referencias PIC a direcciones **absolutas** (no cadenas).

Extiende la regla estricta del repo a cualquier destino (no solo inicios de
cadena) y lista los sitios `add rX,pc` cuyo destino cae en un rango dado.

Uso:  .venv/bin/python analysis/s144_cam_util_sens/scan_pic_abs.py 0x44022d80 0x44022d90
"""
import bisect
import json
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
MAX_LDR_GAP = 4096
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def scan():
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
    out = []
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
        out.append(((w + (a + 4)) & 0xFFFFFFFF, a, la, w))
    return out


if __name__ == "__main__":
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    res = scan()
    hits = [r for r in res if lo <= r[0] < hi]
    print(f"destinos PIC totales={len(res)}  en [{hex(lo)},{hex(hi)})={len(hits)}")
    for dest, a, la, w in sorted(hits):
        print(f"  dest 0x{dest:08x} <- add@0x{a:08x} (ldr@0x{la:08x}, pool=0x{w:08x})")
