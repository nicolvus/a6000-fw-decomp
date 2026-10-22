#!/usr/bin/env python3
"""S119 — busca los `bl` (Thumb) que apuntan a un conjunto de funciones destino.

Uso: python3 find_callers.py 0x439cea30 0x439cebe4 ...
Salida: destino -> [direcciones de los call sites]
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
CODE_LO, CODE_HI = BASE, 0x43C90000

B = open(BIN, "rb").read()


def sign_extend(v, bits):
    if v & (1 << (bits - 1)):
        v -= (1 << bits)
    return v


def main():
    targets = {int(a, 0) for a in sys.argv[1:]}
    o0, o1 = CODE_LO - BASE, CODE_HI - BASE
    seg = B[o0:o1]
    U16 = struct.Struct("<H").unpack_from
    found = {t: [] for t in targets}
    for i in range(0, len(seg) - 4, 2):
        hw1 = U16(seg, i)[0]
        if (hw1 & 0xF800) != 0xF000:
            continue
        hw2 = U16(seg, i + 2)[0]
        if (hw2 & 0xD000) != 0xD000:
            continue
        S = (hw1 >> 10) & 1
        imm10 = hw1 & 0x3FF
        J1 = (hw2 >> 13) & 1
        J2 = (hw2 >> 11) & 1
        imm11 = hw2 & 0x7FF
        I1 = (~(J1 ^ S)) & 1
        I2 = (~(J2 ^ S)) & 1
        imm32 = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1)
        if S:
            imm32 -= (1 << 25)
        addr = CODE_LO + i
        tgt = (addr + 4 + imm32) & 0xFFFFFFFF
        if tgt in found:
            found[tgt].append(addr)
    for t in sorted(found):
        v = found[t]
        print(f"{t:#x}: {len(v)} call sites -> {[hex(x) for x in v[:40]]}")
    json.dump({f"0x{t:x}": [f"0x{x:x}" for x in v] for t, v in found.items()},
              open(os.path.join(HERE, "callers.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
