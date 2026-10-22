#!/usr/bin/env python3
"""S180 - (a) negativo acotado para la linea del obturador
               (b) punteros absolutos de 4 B a las 32 cadenas en los tres firmware
               (c) gemelos: el 'nucleo' sin prefijo en otra posicion.
"""
import json, os, re, struct

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
TERMS = ["shutter", "silent", "curtain", "electro", "mech", "obtur", "sensor", "readout",
         "imager", "iso", "apert", "expos", "expo", "brack", "drive", "release", "flash",
         "sync", "vsync", "frame", "capture", "shot", "rec ", "record", "sweep", "interval",
         "still", "movie", "focus", "exp ", "speed", "shut", "svd", "shd", "spl",
         "ae ", "af ", "aperture", "time", "burst", "wb", "white"]

S = json.load(open("analysis/s180_remote/strings_raw.json"))
A = S["A6000"]
data = {k: open(p, "rb").read() for k, p in BINS.items()}

out = {}
print("=== (a) negativo acotado (32 trazas [REMOTE] de la A6000) ===")
neg = {}
for t in TERMS:
    hits = []
    for s in A:
        if t.lower() in s["text"].lower():
            hits.append(hex(s["vaddr"]))
    neg[t] = hits
    if hits:
        print(f"  {t!r}: {len(hits)} -> {hits}")
out["negativo"] = neg

print()
print("=== (b) punteros absolutos de 4 B a las 32 cadenas ===")
abs_ptrs = {}
for k, d in data.items():
    n = 0
    det = []
    for s in A:
        vb = struct.pack("<I", s["vaddr"])
        c = d.count(vb)
        if c:
            n += c
            det.append({"vaddr": hex(s["vaddr"]), "count": c})
    abs_ptrs[k] = det
    print(f"  {k}: {n} coincidencias en total")
out["abs_ptrs"] = abs_ptrs

print()
print("=== (c) 'nucleo' sin prefijo [ACCY][NIVEL][REMOTE]:%d: en otra posicion ===")
pref = re.compile(r"^\[ACCY\]\[[A-Z]+\]\[REMOTE\]:%d:")
tw = {}
for k, d in data.items():
    lst = []
    for s in A:
        m = pref.match(s["text"])
        if not m:
            continue
        core = s["text"][m.end():].encode("latin1")
        own = s["vaddr"] - BASE + m.end()
        hits = []
        i = d.find(core)
        while i >= 0:
            if i != own:
                hits.append(i + BASE)
            i = d.find(core, i + 1)
        lst.append({"vaddr": hex(s["vaddr"]), "externos": [hex(h) for h in hits]})
    tw[k] = lst
    tot = sum(1 for x in lst if x["externos"])
    print(f"  {k}: {tot}/{len(lst)} con una copia del nucleo FUERA de la cadena prefijada")
out["twins"] = tw

json.dump(out, open("analysis/s180_remote/verify.json", "w"), indent=1)
