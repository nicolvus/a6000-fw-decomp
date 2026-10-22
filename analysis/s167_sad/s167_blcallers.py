#!/usr/bin/env python3
"""S167 — localizadores de `bl` (decodificación Thumb BL/BLX corregida).

Nota: la comprobación `(h2 & 0xD000) in (0x9000,0xD000)` que aparece en
scan_sad.py (y en otros scripts del repo) **pierde las instrucciones BL con J1=0**
(segundo halfword 0xC***).  Aquí se usa la forma correcta:
    BL  : (h2 & 0xD000) & 0xC000 == 0xC000
    BLX : (h2 & 0xD000) & 0xC000 == 0x8000
"""
import struct, sys
BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
U16 = struct.Struct("<H").unpack_from

def bl_sites(lo=BASE, hi=None):
    """[(addr, target)] de todas las instrucciones BL/BLX."""
    if hi is None:
        hi = BASE + len(B) - 4
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        h1 = U16(B, o)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = U16(B, o + 2)[0]
        kind = (h2 & 0xD000) & 0xC000
        if kind == 0xC000:            # BL
            pass
        elif kind == 0x8000:          # BLX (noThumb)
            pass
        else:
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
    return out

if __name__ == "__main__":
    tg = [int(x, 0) for x in sys.argv[1:]]
    sites = bl_sites()
    for t in tg:
        c = [a for a, d in sites if d == t]
        print(f"{t:#x}: {len(c)} llamadores -> {['%#x' % x for x in c]}")
