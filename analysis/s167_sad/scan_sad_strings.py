#!/usr/bin/env python3
"""S167 — localiza las cadenas que contienen el token [SAD] en los tres firmware."""
import json, re, sys

BASE = 0x43541000
BINS = {
    "a6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "a7s_fw320": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300_fw201": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}

def cstrings(data):
    """(offset, texto) de las cadenas imprimibles terminadas en NUL."""
    out = []
    i = 0
    n = len(data)
    while i < n:
        if 32 <= data[i] < 127:
            j = i
            while j < n and 32 <= data[j] < 127:
                j += 1
            if j < n and data[j] == 0 and j - i >= 4:
                out.append((i, data[i:j].decode("ascii")))
            i = j + 1
        else:
            i += 1
    return out

res = {}
for tag, path in BINS.items():
    data = open(path, "rb").read()
    hits = [(off, s) for off, s in cstrings(data) if "[SAD]" in s]
    res[tag] = [{"off": off, "vaddr": off + BASE, "text": s} for off, s in hits]
    res[tag + "_count_token"] = sum(s.count("[SAD]") for _, s in hits)
    print(tag, "cadenas con [SAD]:", len(hits), "apariciones:", res[tag + "_count_token"])

json.dump(res, open("analysis/s167_sad/sad_strings_raw.json", "w"), indent=1)
for h in res["a6000_fw321"]:
    print(f"{h['vaddr']:#x}  {h['text']!r}")
