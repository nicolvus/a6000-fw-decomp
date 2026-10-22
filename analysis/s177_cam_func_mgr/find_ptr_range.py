#!/usr/bin/env python3
"""S177 — busca en toda la imagen cualquier u32 LE dentro de un rango dado.

Uso: find_ptr_range.py <lo> <hi> [fw]
"""
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
fw = sys.argv[3] if len(sys.argv) > 3 else "A6000"
lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
hits = []
for v in range(lo, hi + 1):
    pat = struct.pack("<I", v)
    i = B.find(pat)
    while i >= 0:
        hits.append((v, i + BASE))
        i = B.find(pat, i + 1)
for v, a in sorted(hits):
    print(f"valor={v:#x} en {a:#x}")
print(len(hits), "coincidencias")
