#!/usr/bin/env python3
"""CAM-01: ¿alguna cadena de av-cam expande una sigla? (patrón: palabras consecutivas con esas iniciales, o `SIGLA (`/`SIGLA =`/`SIGLA:` seguida de texto largo)."""
import json, re, sys
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
S = [m.group().decode() for m in re.finditer(rb"[\x20-\x7e]{8,}", B)]
ACR = "CC LC TC APL HW SA HME MMU SHD ITP DCV OLC CLP PFR ZDL OAC OPB ARC RC DIST AS DDT STC EIS IS FC IM YC SMART".split()
out = {}
for a in ACR:
    pat = re.compile(r"\b" + r"[a-z]+\s+".join(c for c in a) .replace(a[0], a[0], 1) + r"[a-z]+\b" if False else
                     r"\b" + r"\s+".join(f"{c}[a-z]{{2,}}" for c in a) + r"\b")
    hits = sorted({m.group() for s in S for m in [pat.search(s)] if m and len(a) >= 2})
    out[a] = hits[:6]
    print(a, len(hits), hits[:4])
json.dump(out, open("analysis/camera_closure/acronyms.json", "w"), indent=1)
