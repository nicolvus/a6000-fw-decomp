#!/usr/bin/env python3
"""S177 — vuelca una tabla de punteros absolutos (u32 LE) y resuelve cada entrada.

Uso: dump_ptrtable.py <lo> <hi> [fw]
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
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
N = len(B)


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0 or e - o > 200:
        return None
    try:
        s = B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
for a in range(lo, hi, 4):
    v = struct.unpack_from("<I", B, a - BASE)[0]
    s = cstr(v) if v else None
    print(f"{a:#x}  {v:#010x}  {s!r}")
