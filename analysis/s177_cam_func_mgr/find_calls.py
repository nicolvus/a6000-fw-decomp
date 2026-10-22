#!/usr/bin/env python3
"""S177 — encuentra las llamadas `bl` a un objetivo (Thumb BL/BLX) en la imagen.

Uso: find_calls.py <target> [fw]
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
fw = sys.argv[2] if len(sys.argv) > 2 else "A6000"
target = int(sys.argv[1], 0)
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
hits = []
a = BASE
while a < BASE + N:
    o = a - BASE
    if o < 0 or o > N - 4:
        a += 2
        continue
    h = U16(B, o)[0]
    if (h & 0xF800) == 0xF000:
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
                hits.append(a)
        a += 4
        continue
    a += 2
print(f"bl {target:#x}: {len(hits)} llamadas -> " +
      ", ".join(hex(h) for h in hits[:40]))
