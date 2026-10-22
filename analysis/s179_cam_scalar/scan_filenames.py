#!/usr/bin/env python3
"""S179 - nombres de fichero y RTTI alrededor de la zona de [CAM_SCALAR]."""
import json, os, re
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
G=json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
out=[]
for k,sites in G.items():
    a=int(k,16); o=a-BASE; e=o
    while e<len(B) and 32<=B[e]<127: e+=1
    t=B[o:e].decode("latin1")
    if re.search(r"\.(cpp|c|h|hpp)$", t) or t.startswith("N6Camera") or t.startswith("N15") or "/src/" in t:
        out.append((min(sites), a, t, sorted(sites)))
out.sort()
for s,a,t,ss in out:
    if 0x43800000 <= s < 0x43900000:
        print(f"str 0x{a:08x}  site0x{s:08x}  {t}")
