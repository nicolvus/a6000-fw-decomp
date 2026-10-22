#!/usr/bin/env python3
"""S179 - negativo acotado para la linea del obturador + terminos de interes."""
import json, re
BASE=0x43541000
B=open("analysis/rea-independent/input/av-cam.bin","rb").read()
S=json.load(open("analysis/s179_cam_scalar/strings_raw.json"))["A6000"]
TERMS=["shutter","silent","curtain","electro","mech","obtur","expos","iso","apert","sensor","readout",
 "shut","svd","shd","spl","frame","imager","drive","brack","sweep","interval","still","movie","focus",
 "ae ","af ","sync","vsync","fseq","scan","ev "," shutter"]
txts=[s["text"] for s in S]
blob="\n".join(txts)
for t in TERMS:
    hits=[(s["vaddr"],s["text"]) for s in S if t.lower() in s["text"].lower()]
    print(f"{t:12s} {len(hits):2d}  " + "; ".join(f"0x{a:x}: {x[:60]}" for a,x in hits))
print()
# palabras sueltas que SI aparecen
for w in ["ExposureCount","RecordCount","CapMode","CAP_SINGLE","DMM","RAW","YC","SDS","HAPI","NR Level"]:
    hits=[(s["vaddr"],s["text"]) for s in S if w in s["text"]]
    print(f"{w:14s} {len(hits)}")
