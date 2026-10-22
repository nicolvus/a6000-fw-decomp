#!/usr/bin/env python3
"""S156 — escáner rápido de llamadas directas BL (Thumb) en la imagen.

Decodifica el par de medios-palabras del par de la instrucción BL de 32 bits
de Thumb-2 sin usar Capstone (barriento los ~11,4 MB en segundos).
"""
import struct
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from common import BASE, B, N, U16  # noqa: E402

U32 = struct.Struct("<I").unpack_from


def bl_sites(lo=BASE, hi=BASE + N):
    """[(addr, target)] de todas las BL de 32 bits."""
    out = []
    a = lo
    a &= ~1
    while a < hi - 3:
        h1 = U16(B, a - BASE)[0]
        if (h1 & 0xF800) == 0xF000:
            h2 = U16(B, a - BASE + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h1 >> 10) & 1
                imm10 = h1 & 0x3FF
                i1 = (h2 >> 13) & 1
                i2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                j1 = (~(i1 ^ s)) & 1
                j2 = (~(i2 ^ s)) & 1
                imm = (s << 24) | (j1 << 23) | (j2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    imm -= 1 << 25          # SignExtend de 25 bits (bit24 = S)
                tgt = (a + 4) + imm
                out.append((a, tgt & 0xFFFFFFFF))
                a += 4
                continue
        a += 2
    return out


def callers(target, lo=BASE, hi=BASE + N):
    return [a for a, t in bl_sites(lo, hi) if t == target]


if __name__ == "__main__":
    for t in sys.argv[1:]:
        tgt = int(t, 0)
        cs = callers(tgt)
        print(f"=== callers de {tgt:#x}: {len(cs)} ===")
        for c in cs:
            print(f"  {c:#x}")
