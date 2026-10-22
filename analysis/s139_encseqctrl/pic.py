#!/usr/bin/env python3
"""Resuelve un `add rX, pc` de 16 bits: devuelve (reg, destino, literal, W).

El destino = W + (dirección_del_add + 4), donde W es la palabra del pool de
literales a la que apunta el `ldr rX,[pc,#imm]` más cercano por detrás.

Uso: .venv/bin/python analysis/s139_encseqctrl/pic.py 0x435d70aa [0x435d70aa ...]
"""
import os
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()


def hw(a):
    return struct.unpack_from("<H", B, a - BASE)[0]


def w32(a):
    return struct.unpack_from("<I", B, a - BASE)[0]


def resolve(site, window=0x200):
    h = hw(site)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 0xF, hex(h)
    rd = ((h >> 7) & 1) << 3 | (h & 7)
    for a in range(site - 2, site - window, -2):
        h1 = hw(a)
        if (h1 & 0xF800) == 0x4800 and ((h1 >> 8) & 7) == rd:
            lit = ((a + 4) & ~3) + (h1 & 0xFF) * 4
            w = w32(lit)
            return {"add": hex(site), "reg": rd, "ldr": hex(a), "literal": hex(lit),
                    "W": hex(w), "destino": hex((w + site + 4) & 0xFFFFFFFF)}
    for a in range(site - 4, site - window, -2):
        if hw(a) == 0xF8DF:
            h2 = hw(a + 2)
            if (h2 >> 12) != rd:
                continue
            imm = ((h2 >> 8) & 0xF) << 8 | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm
            w = w32(lit)
            return {"add": hex(site), "reg": rd, "ldr": hex(a), "literal": hex(lit),
                    "W": hex(w), "destino": hex((w + site + 4) & 0xFFFFFFFF)}
    return None


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(resolve(int(s, 0)))
