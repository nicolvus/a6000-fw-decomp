#!/usr/bin/env python3
"""S170 — busca llamadas (BL/BLX) a una dirección dada en un rango de código.

Uso:  find_calls.py 0x435acdd0 [LO] [HI]
"""
import struct
import sys

BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def sign_extend(v, bits):
    v &= (1 << bits) - 1
    if v & (1 << (bits - 1)):
        v -= (1 << bits)
    return v


def find_calls(target, lo=0x43541000, hi=0x44017000):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0xF000:
            # BL (T1): 11110 S imm10 | 11 J1 1 J2 imm11
            h2 = U16(B, o + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h >> 10) & 1
                imm10 = h & 0x3FF
                j1 = (h2 >> 13) & 1
                j2 = (h2 >> 11) & 1
                imm11 = h2 & 0x7FF
                i1 = 1 - (j1 ^ s)
                i2 = 1 - (j2 ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
                if s:
                    imm -= (1 << 25)
                dst = a + 4 + imm
                if dst == target:
                    out.append(a)
            a += 4
            continue
        a += 2
    return out


if __name__ == "__main__":
    t = int(sys.argv[1], 0)
    lo = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x43541000
    hi = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x44017000
    for c in find_calls(t, lo, hi):
        print(hex(c))
