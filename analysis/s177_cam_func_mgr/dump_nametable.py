#!/usr/bin/env python3
"""S177 — vuelca la tabla de nombres del gestor de funciones (entradas de 12 B).

Uso: dump_nametable.py <base> <n> [fw]
"""
import json
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
base = int(sys.argv[1], 0)
n = int(sys.argv[2], 0)
entries = []
for i in range(n):
    a = base + 12 * i
    p, idv, pad = struct.unpack_from("<III", B, a - BASE)
    o = p - BASE
    name = None
    if 0 <= o < len(B):
        e = B.find(b"\x00", o)
        if 0 <= e - o < 120:
            try:
                s = B[o:e].decode("ascii")
                if all(32 <= ord(c) < 127 for c in s):
                    name = s
            except UnicodeDecodeError:
                pass
    entries.append({"slot": hex(a), "nombre": name, "id": idv, "id_hex": hex(idv),
                    "pad": pad})
    print(f"{a:#x}  name={name!r}  id={idv:#06x}  pad={pad:#x}")
json.dump(entries, open(os.path.join(
    ROOT, f"analysis/s177_cam_func_mgr/cfm_nametable_{fw}.json"), "w"), indent=1)
