#!/usr/bin/env python3
"""S179 - sitios PIC (regla estricta) de las cadenas [CAM_SCALAR] desde el mapa global."""
import json

BASE = 0x43541000
G = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
S = json.load(open("analysis/s179_cam_scalar/strings_raw.json"))["A6000"]

out = {}
for s in S:
    k = "0x%x" % s["vaddr"]
    sites = G.get(k, [])
    out[k] = {"text": s["text"], "sites": ["0x%x" % x for x in sorted(set(sites))]}
    print(f"{k}  n={len(sites):2d}  {s['text'][:70]}")
    for x in sorted(set(sites)):
        print(f"      -> 0x{x:08x}")

json.dump(out, open("analysis/s179_cam_scalar/pic_sites.json", "w"), indent=1)
tot = sum(len(v["sites"]) for v in out.values())
print("TOTAL sitios:", tot, " cadenas con ref:", sum(1 for v in out.values() if v["sites"]))
