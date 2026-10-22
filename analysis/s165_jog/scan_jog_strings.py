#!/usr/bin/env python3
"""Extrae las cadenas [JOG] del firmware A6000 fw3.21 (y diferenciales A7S/A6300)."""
import json, re, sys

BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300_fw201": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
PAT = re.compile(rb"\[[A-Za-z_][A-Za-z0-9_]*\]")

def strings_with_prefix(b, pref):
    out = []
    pat = pref.encode()
    start = 0
    while True:
        i = b.find(pat, start)
        if i < 0:
            break
        # retroceder hasta el inicio de la cadena
        j = i
        while j > 0 and 32 <= b[j-1] < 127:
            j -= 1
        k = i
        while k < len(b) and 32 <= b[k] < 127:
            k += 1
        out.append((j, b[j:k].decode("ascii", "replace")))
        start = i + 1
    return out

res = {}
for name, path in FILES.items():
    try:
        b = open(path, "rb").read()
    except FileNotFoundError:
        res[name] = {"error": "no existe"}
        continue
    hits = strings_with_prefix(b, "[JOG]")
    # dedup
    seen = {}
    for off, s in hits:
        seen.setdefault(s, off)
    res[name] = {
        "path": path,
        "size": len(b),
        "strings": [{"file_offset": hex(o), "vaddr": hex(o + BASE), "text": s}
                    for s, o in sorted(seen.items(), key=lambda kv: kv[1])],
    }
    print(name, len(seen), "cadenas unicas")

# recuento total de ocurrencias brutas en A6000
b = open(FILES["A6000_fw321"], "rb").read()
occ = [m.start() for m in re.finditer(rb"\[JOG\]", b)]
print("ocurrencias brutas A6000 [JOG]:", len(occ), [hex(o) for o in occ])
json.dump(res, open("analysis/s165_jog/jog_strings_raw.json", "w"), indent=1)
