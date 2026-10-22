#!/usr/bin/env python3
"""S170 — inventario textual de "Illumi" y de nombres de fichero fuente vecinos.

Busca en toda la imagen A6000 (y en A7S/A6300) todas las cadenas ASCII que
contienen "Illumi" (RTTI, __PRETTY_FUNCTION__, trazas) y lista los nombres de
fichero fuente (*.cpp/*.h) referenciados en la zona de código del módulo.
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
PAT = re.compile(rb"[\x20-\x7e]{4,}")


def strings(b, needle):
    out = []
    for m in PAT.finditer(b):
        s = m.group().decode("ascii")
        if needle in s:
            out.append((m.start(), s))
    return out


res = {}
for name, path in FILES.items():
    b = open(path, "rb").read()
    hits = strings(b, "Illumi")
    res[name] = [{"vaddr": hex(o + BASE), "texto": s} for o, s in hits]
    print(f"== {name}: {len(hits)} cadenas con 'Illumi'")
    for o, s in hits:
        print(f"   {o + BASE:#x} {s!r}")

json.dump(res, open("analysis/s170_illumi/illumi_names.json", "w"), indent=1)
