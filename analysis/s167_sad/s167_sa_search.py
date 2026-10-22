#!/usr/bin/env python3
"""S167 — búsqueda de la sigla SA/SAD en las cadenas del firmware."""
import re
BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
PATS = [
    rb"\bSA[0-9_]", rb"_SA\b", rb"\bSA\b", rb"Sa[A-Z][A-Za-z]*", rb"SAD",
    rb"\bZM[0-9_]", rb"ScalarInfra", rb"NS_SCALAR",
]
seen = {}
for m in re.finditer(rb"[\x20-\x7e]{3,}", B):
    s = m.start()
    e = B.find(b"\x00", s)
    t = B[s:e]
    for p in PATS:
        if re.search(p, t):
            seen.setdefault(p.decode(), []).append((BASE + s, t.decode("latin1")))
            break
for p in PATS:
    lst = seen.get(p.decode(), [])
    print(f"### {p.decode()}  -> {len(lst)}")
    for a, t in lst[:80]:
        print(f"   {a:#x} {t!r}")
