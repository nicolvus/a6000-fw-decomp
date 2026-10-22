#!/usr/bin/env python3
"""S167 — sitios PIC de las cadenas [SAD] con la regla estricta (mapa global canónico)."""
import json

GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
gm = {int(k, 16): sorted(set(v)) for k, v in json.load(open(GLOBAL)).items()}
raw = json.load(open("analysis/s167_sad/sad_raw.json"))
cad = raw["cadenas"]
tot = 0
for c in cad:
    a = c["vaddr"]
    s = gm.get(a, [])
    tot += len(s)
    print(f"{a:#x} n={len(s)} {c['texto']!r}")
    for x in s:
        print(f"      sitio {x:#x}")
print("TOTAL sitios:", tot, "cadenas:", len(cad),
      "sin ref:", sum(1 for c in cad if not gm.get(c['vaddr'])))
