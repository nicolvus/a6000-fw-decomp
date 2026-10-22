#!/usr/bin/env python3
"""S179 — cadenas referenciadas por PIC desde la zona de codigo de [CAM_SCALAR]."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
G = json.load(open(os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")))
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()

LO, HI = 0x43808000, 0x438d0000
rows = []
for k, sites in G.items():
    a = int(k, 16)
    ss = sorted(int(x) for x in sites)
    ins = [x for x in ss if LO <= x < HI]
    if not ins:
        continue
    o = a - BASE
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    txt = B[o:e].decode("latin1")
    rows.append((a, ss, ins, txt))
rows.sort()
out = []
for a, ss, ins, txt in rows:
    print(f"0x{a:08x}  tot={len(ss):3d} in-region={len(ins):3d}  {txt[:110]}")
    out.append({"vaddr": "0x%x" % a, "sitios": ["0x%x" % x for x in ins], "todos_sitios": ["0x%x" % x for x in ss], "texto": txt})
json.dump(out, open(os.path.join(ROOT, "analysis/s179_cam_scalar/region_strings.json"), "w"), indent=1)
print("total", len(out))
