#!/usr/bin/env python3
"""S177 — busca punteros absolutos (u32 LE) a direcciones concretas en la imagen.

Uso: find_ptrs.py <addr1> [addr2 ...] [fw]
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
args = sys.argv[1:]
fw = "A6000"
if args and args[-1] in FILES:
    fw = args.pop()
addrs = [int(a, 0) for a in args]
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
N = len(B)
for a in addrs:
    pat = struct.pack("<I", a)
    hits = []
    i = 0
    while True:
        j = B.find(pat, i)
        if j < 0:
            break
        hits.append(j + BASE)
        i = j + 1
    print(f"{a:#x}: {len(hits)} punteros -> " +
          ", ".join(hex(h) for h in hits[:24]))
