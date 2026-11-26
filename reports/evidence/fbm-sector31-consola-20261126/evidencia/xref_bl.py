#!/usr/bin/env python3
"""Llamantes `bl`/`blx` (decodificación manual del par de halfwords Thumb-2, túnel de datos incluido)
de una lista de VA en libmpr.so."""
import struct
import sys
sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M

TEXT = M.sec(".text")
code = M.rd(TEXT[0], TEXT[1] - TEXT[0])


def sxt(v, bits):
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def bl_target(off):
    h1, h2 = struct.unpack_from("<HH", code, off)
    if (h1 & 0xF800) != 0xF000:
        return None
    S = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    if (h2 & 0xD000) == 0xD000:                       # bl
        J1, J2 = (h2 >> 13) & 1, (h2 >> 11) & 1
        I1, I2 = 1 - (J1 ^ S), 1 - (J2 ^ S)
        imm = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | ((h2 & 0x7FF) << 1)
        return (TEXT[0] + off + 4 + sxt(imm, 25)) & ~1
    if (h2 & 0xD000) == 0xC000:                       # blx (imm)
        I1, I2 = 1 - (((h2 >> 13) & 1) ^ S), 1 - (((h2 >> 11) & 1) ^ S)
        imm = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | ((h2 & 0x7FE) << 1)
        return (TEXT[0] + off + 4 + sxt(imm, 25)) & ~3
    return None


objetivo = {int(a, 0): [] for a in sys.argv[1:]}
for off in range(0, len(code) - 4, 2):
    t = bl_target(off)
    if t in objetivo:
        objetivo[t].append(TEXT[0] + off)
for t, l in objetivo.items():
    print(f"{t:#x}: {len(l)} llamantes -> " + ", ".join(f"{x:#x}" for x in l[:10]) + (" ..." if len(l) > 10 else ""))
