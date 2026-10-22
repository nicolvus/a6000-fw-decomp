#!/usr/bin/env python3
"""S139 — llamadores `bl` directos (decodificación manual del patrón de 32 bits).

No usa desensamblado lineal: en zonas con datos intercalados Capstone se
desincroniza y pierde llamadas. El patrón de bits 11110...11...1 es inequívoco
y se busca en todas las fronteras de media palabra del rango de código.

Uso: .venv/bin/python analysis/s139_encseqctrl/callers.py 0x435d715c [0x...]
"""
import os
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
CODE_LO, CODE_HI = 0x43541000, 0x43A00000


def callers(targets):
    out = {t: [] for t in targets}
    tset = set(targets)
    for a in range(CODE_LO, CODE_HI - 4, 2):
        h1 = struct.unpack_from("<H", B, a - BASE)[0]
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = struct.unpack_from("<H", B, a - BASE + 2)[0]
        if (h2 & 0xD000) not in (0x9000, 0xD000):
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        tgt = (a + 4 + imm) & 0xFFFFFFFF
        if tgt in tset:
            out[tgt].append(a)
    return out


if __name__ == "__main__":
    tg = [int(x, 0) for x in sys.argv[1:]]
    r = callers(tg)
    for t in tg:
        print(f"0x{t:x}: " + ", ".join(hex(x) for x in r[t]))
