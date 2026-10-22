#!/usr/bin/env python3
"""S151: localiza las cadenas [PANDA] en los tres av-cam.bin y en el resto del blob."""
import json, os, re, sys

BASE = 0x43541000
BLOBS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

def find_all(blob, needle):
    out = []
    start = 0
    while True:
        i = blob.find(needle, start)
        if i < 0:
            break
        out.append(i)
        start = i + 1
    return out

def cstr(blob, off, limit=400):
    e = blob.find(b"\x00", off)
    if e < 0 or e - off > limit:
        e = min(len(blob), off + limit)
    return blob[off:e].decode("utf-8", "replace")

res = {}
for name, path in BLOBS.items():
    blob = open(path, "rb").read()
    hits = find_all(blob, b"[PANDA]")
    chains = []
    for h in hits:
        # inicio de la cadena: retroceder hasta el NUL previo
        s = blob.rfind(b"\x00", 0, h)
        s = s + 1 if s >= 0 else 0
        chains.append({"hit_off": h, "str_off": s, "vaddr": BASE + s, "text": cstr(blob, s)})
    # deduplicar por inicio de cadena
    seen = {}
    for c in chains:
        seen.setdefault(c["str_off"], c)
    res[name] = {"n_bytes": len(blob), "n_hits": len(hits), "cadenas": sorted(seen.values(), key=lambda x: x["vaddr"])}
    print(f"{name}: {len(hits)} ocurrencias de '[PANDA]', {len(seen)} cadenas")
    for c in sorted(seen.values(), key=lambda x: x["vaddr"]):
        print(f"   0x{c['vaddr']:08x}  {c['text']!r}")

json.dump(res, open("analysis/s151_panda/strings_panda.json", "w"), indent=1, ensure_ascii=False)
