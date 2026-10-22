#!/usr/bin/env python3
"""S180 - volcar un pool de literales (dwords) de los tres firmware."""
import struct, sys

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
RANGES = {
    "A6000": [(0x435667e8, 0x43566810), (0x43566cf0, 0x43566d20)],
    "A7S": [(0x4356486c, 0x43564894), (0x43564b20, 0x43564b58)],
    "A6300": [(0x4355f038, 0x4355f060), (0x4355f320, 0x4355f358)],
}
for k, p in BINS.items():
    d = open(p, "rb").read()
    print("=" * 66)
    print(k)
    for lo, hi in RANGES[k]:
        print(f"  pool 0x{lo:08x}-0x{hi:08x}")
        for a in range(lo, hi, 4):
            v = struct.unpack_from("<I", d, a - BASE)[0]
            print(f"    0x{a:08x}  0x{v:08x}")
