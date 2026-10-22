#!/usr/bin/env python3
"""S170 — extrae las cadenas [ILLUMI] del firmware A6000 fw3.21 (y diferenciales A7S/A6300).

Sólo bytes. Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import re

BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
TOKEN = b"[ILLUMI]"


def strings_with_token(b, tok):
    """[(file_offset, texto)] de las cadenas ASCII que contienen `tok`."""
    out = []
    start = 0
    while True:
        i = b.find(tok, start)
        if i < 0:
            break
        j = i
        while j > 0 and 32 <= b[j - 1] < 127:
            j -= 1
        k = i
        while k < len(b) and 32 <= b[k] < 127:
            k += 1
        out.append((j, b[j:k].decode("ascii", "replace")))
        start = i + 1
    return out


res = {}
for name, path in FILES.items():
    b = open(path, "rb").read()
    hits = strings_with_token(b, TOKEN)
    seen = {}
    for off, s in hits:
        seen.setdefault(s, off)
    occ = [m.start() for m in re.finditer(re.escape(TOKEN), b)]
    res[name] = {
        "path": path,
        "size": len(b),
        "n_ocurrencias_token": len(occ),
        "n_cadenas_unicas": len(seen),
        "cadenas": [{"file_offset": hex(o), "vaddr": hex(o + BASE), "texto": s}
                    for s, o in sorted(seen.items(), key=lambda kv: kv[1])],
        "ocurrencias_brutas": [hex(o + BASE) for o in occ],
    }
    print(f"{name}: {len(occ)} ocurrencias brutas, {len(seen)} cadenas unicas")

json.dump(res, open("analysis/s170_illumi/illumi_strings_raw.json", "w"), indent=1)
print("escrito analysis/s170_illumi/illumi_strings_raw.json")
