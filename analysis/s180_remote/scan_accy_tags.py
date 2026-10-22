#!/usr/bin/env python3
"""S180 - inventario de sub-etiquetas [ACCY][*] en los tres firmware."""
import os, re, json
from collections import Counter

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

pat = re.compile(rb"\[ACCY\]\[([A-Z_]+)\]")

for k, p in BINS.items():
    d = open(p, "rb").read()
    c = Counter(m.group(1).decode() for m in pat.finditer(d))
    print(f"== {k}: total [ACCY] = {d.count(b'[ACCY]')}")
    for tag, n in c.most_common():
        print(f"   [{tag}] x{n}")
