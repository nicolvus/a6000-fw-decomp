#!/usr/bin/env python3
"""S140 - escaneo PIC "sin filtro de inicio de cadena": calcula TODOS los
destinos `add rX,pc` (regla estricta) y busca los que caen en un rango dado.

Sirve para localizar tablas de datos (p.ej. la tabla de codigos "Sens:*") que no
aparecen en pic_refs_strict_global.json porque ese mapa solo guarda destinos
que son inicio de cadena.

Uso: python scan_pic_range.py LO HI
"""
import bisect
import json
import os
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
MAX_LDR_GAP = 4096

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def scan(lo, hi):
    ldrs = []
    adds = []
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
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= N - 4:
                ldrs.append((a, reg, U32(B, o2)[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
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
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        out.append(((w + (a + 4)) & 0xFFFFFFFF, a, la))
    return out


if __name__ == "__main__":
    lo_t = int(sys.argv[1], 0)
    hi_t = int(sys.argv[2], 0)
    res = scan(BASE, BASE + N)
    hits = [r for r in res if lo_t <= r[0] < hi_t]
    print(f"destinos PIC totales={len(res)}  en rango [{hex(lo_t)},{hex(hi_t)}]={len(hits)}")
    for dest, a, la in sorted(hits):
        print(f"  dest 0x{dest:08x}  <- add@0x{a:08x} (ldr@0x{la:08x})")
    json.dump([{"dest": f"0x{d:08x}", "add": f"0x{a:08x}", "ldr": f"0x{l:08x}"}
               for d, a, l in sorted(hits)],
              open(os.path.join(REPO, "analysis/s140_cam_util_adj/pic_range_hits.json"), "w"),
              indent=1)
