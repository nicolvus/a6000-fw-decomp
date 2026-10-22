#!/usr/bin/env python3
"""S180 - buscar los codigos de tecla del mando (0x0A0000xx) en los tres firmware."""
import struct, json

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
KEYS = [0x0A000008, 0x0A000009, 0x0A00000C, 0x0A00000D, 0x0A000011]

out = {}
for k, p in BINS.items():
    d = open(p, "rb").read()
    print("=" * 60)
    print(k)
    r = {}
    for key in KEYS:
        kb = struct.pack("<I", key)
        hits = []
        i = d.find(kb)
        while i >= 0:
            hits.append(i + BASE)
            i = d.find(kb, i + 1)
        r[f"0x{key:08x}"] = [hex(h) for h in hits]
        print(f"  0x{key:08x}: {len(hits)} -> {[hex(h) for h in hits]}")
    out[k] = r
json.dump(out, open("analysis/s180_remote/keycodes.json", "w"), indent=1)
