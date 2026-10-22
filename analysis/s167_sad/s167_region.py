#!/usr/bin/env python3
"""S167 — todas las cadenas referenciadas (PIC estricto) en un rango de código,
para deducir ficheros fuente / clases del módulo."""
import json, sys, re
BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin","rb").read()
gm = {int(k,16): sorted(set(v)) for k,v in json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json")).items()}
lo, hi = int(sys.argv[1],0), int(sys.argv[2],0)
def cstr(a):
    o=a-BASE
    if o<0 or o>=len(B): return None
    e=B.find(b"\x00",o); return B[o:e].decode("latin1")
files=set(); rtti=set(); other={}
for dest, sites in gm.items():
    for s in sites:
        if not (lo<=s<hi): continue
        t=cstr(dest)
        if t is None: continue
        if t.endswith(".cpp") or t.endswith(".h") or ".cpp:" in t or ".h:" in t:
            files.add((dest,t))
        elif re.match(r"^N\d+\w+", t) or "E" == t[-1:] and t.startswith("N"):
            rtti.add((dest,t))
        else:
            other.setdefault(dest,[]).append((s,t))
print("### ficheros fuente")
for d,t in sorted(files): print(f"  {d:#x} {t[:120]!r}")
print("### RTTI")
for d,t in sorted(rtti): print(f"  {d:#x} {t[:120]!r}")
print(f"### otras cadenas distintas: {len(other)}")
for d,v in sorted(other.items()):
    print(f"  {d:#x} {v[0][1][:100]!r}  x{len(v)}")
