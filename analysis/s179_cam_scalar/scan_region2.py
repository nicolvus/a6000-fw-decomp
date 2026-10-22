#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
G = json.load(open(os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")))
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()
LO = int(sys.argv[1],0); HI = int(sys.argv[2],0)
rows=[]
for k, sites in G.items():
    a = int(k,16); ss = sorted(int(x) for x in sites)
    ins=[x for x in ss if LO<=x<HI]
    if not ins: continue
    o=a-BASE; e=o
    while e<len(B) and 32<=B[e]<127: e+=1
    rows.append((min(ins),a,ins,B[o:e].decode('latin1')))
rows.sort()
for s,a,ins,txt in rows:
    print(f"sitio0x{s:08x} str 0x{a:08x} n={len(ins)}  {txt[:120]}")
