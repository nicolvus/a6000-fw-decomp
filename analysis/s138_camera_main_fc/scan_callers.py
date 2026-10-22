#!/usr/bin/env python3
"""S138 — llamaadores (`bl` directos) de un conjunto de funciones, en toda la imagen.

Uso: .venv/bin/python analysis/s138_camera_main_fc/scan_callers.py 0x437b7200 0x437b74a4 ...
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
IMG_LO, IMG_HI = BASE, BASE + len(B)


def callers(targets):
    """{target: [sitios bl]} para `bl` directos en toda la imagen."""
    tset = set(targets)
    out = {t: [] for t in targets}
    for a in range(IMG_LO, IMG_HI - 4, 2):
        o = a - BASE
        h1, h2 = struct.unpack_from("<HH", B, o)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        d = (a + 4 + s) & 0xFFFFFFFF
        if d in tset:
            out[d].append(a)
    return out


def main():
    targets = [int(x, 16) for x in sys.argv[1:]]
    res = callers(targets)
    for t in targets:
        s = res[t]
        print(f"0x{t:x}: {len(s)} llamadores  {[hex(x) for x in s]}")
    json.dump({f"0x{t:x}": [f"0x{x:x}" for x in res[t]] for t in targets},
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_callers.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
