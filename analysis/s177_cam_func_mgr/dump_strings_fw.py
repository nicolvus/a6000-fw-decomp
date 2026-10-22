#!/usr/bin/env python3
"""S177 — volcado de cadenas ASCII en un rango de vaddr para un firmware dado.

Uso: dump_strings_fw.py <fw> <lo> <hi>
"""
import os
import re
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
fw = sys.argv[1]
B = open(os.path.join(ROOT, FILES[fw]), "rb").read()
lo = int(sys.argv[2], 0)
hi = int(sys.argv[3], 0)
for m in re.finditer(rb"[\x20-\x7e]{3,}", B[lo - BASE:hi - BASE]):
    print(f"{lo - BASE + m.start() + BASE:#x}  {m.group().decode('ascii')}")
