#!/usr/bin/env python3
"""S138 — localiza las cadenas del módulo `[CAMERA_MAIN_FC]` en los tres firmwares.

Salida: JSON con las cadenas (texto completo), su vaddr y el byte inicial.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000

FW = {
    "a6000": os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"),
    "a7s": os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def find_all(data, needle):
    out = []
    i = data.find(needle)
    while i != -1:
        out.append(i)
        i = data.find(needle, i + 1)
    return out


def cstring(data, off):
    e = data.find(b"\x00", off)
    if e == -1:
        e = len(data)
    return data[off:e].decode("utf-8", "replace")


def main():
    token = sys.argv[1].encode() if len(sys.argv) > 1 else b"[CAMERA_MAIN_FC]"
    res = {}
    for name, path in FW.items():
        data = open(path, "rb").read()
        offs = find_all(data, token)
        items = []
        for o in offs:
            items.append({
                "file_offset": o,
                "vaddr": BASE + o,
                "text": cstring(data, o),
            })
        res[name] = {"size": len(data), "occurrences": len(offs), "items": items}
        print(f"{name}: {len(offs)} apariciones de {token!r}")
        for it in items:
            print(f"   0x{it['vaddr']:08x}  {it['text'][:120]!r}")
    dest = os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_strings.json")
    with open(dest, "w") as fh:
        json.dump(res, fh, indent=1)
    print("->", dest)


if __name__ == "__main__":
    main()
