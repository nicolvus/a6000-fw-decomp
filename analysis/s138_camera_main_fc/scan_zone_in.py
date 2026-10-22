#!/usr/bin/env python3
"""S138 — mapa de llamadas entrantes a una zona de código (todo `bl` de la imagen).

Uso: .venv/bin/python analysis/s138_camera_main_fc/scan_zone_in.py 0x437b6000 0x437b8400
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    out = {}
    for a in range(BASE, BASE + len(B) - 4, 2):
        o = a - BASE
        h1, h2 = struct.unpack_from("<HH", B, o)
        if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        d = (a + 4 + s) & 0xFFFFFFFF
        if lo <= d < hi:
            out.setdefault(d, []).append(a)
    for d in sorted(out):
        cs = out[d]
        print(f"0x{d:x}: {len(cs)} llamadores  {[hex(c) for c in cs]}")
    json.dump({f"0x{d:x}": [f"0x{c:x}" for c in out[d]] for d in sorted(out)},
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_zone_in.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
