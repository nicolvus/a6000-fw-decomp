#!/usr/bin/env python3
"""S180 - referencias PIC (mapa global) + gemelos del 'nucleo' en los tres firmware.

Un 'gemelo' es una aparicion del texto SIN el prefijo `[ACCY][NIVEL][REMOTE]:%d:`
en una posicion distinta de la propia cadena prefijada.
"""
import json, os, re

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"

STR = json.load(open("analysis/s180_remote/strings_raw.json"))
A = STR["A6000"]
pic = json.load(open(GLOBAL))
pref_re = re.compile(r"^\[ACCY\]\[[A-Z]+\]\[REMOTE\]:%d:")

recs = []
for s in A:
    t = s["text"]
    m = pref_re.match(t)
    core = t[m.end():] if m else None
    v = s["vaddr"]
    sites = pic.get(f"0x{v:x}", [])
    recs.append({
        "vaddr": v, "text": t,
        "level": re.match(r"^\[ACCY\]\[([A-Z]+)\]", t).group(1),
        "prefix_len": m.end() if m else None,
        "core": core,
        "pic_sites": sites, "n_pic": len(sites),
    })

data = {k: open(p, "rb").read() for k, p in BINS.items()}

twins = {}
for name, d in data.items():
    lst = []
    for r in recs:
        cb = r["core"].encode("latin1")
        hits = []
        i = d.find(cb)
        while i >= 0:
            hits.append(i)
            i = d.find(cb, i + 1)
        own = r["vaddr"] - BASE
        # posicion del core DENTRO de la propia cadena prefijada
        inside = own + r["prefix_len"]
        ext = [h for h in hits if h != inside]
        lst.append({"vaddr": r["vaddr"], "core": r["core"], "n_hits": len(hits),
                    "hits": [h + BASE for h in hits],
                    "external": [h + BASE for h in ext]})
    twins[name] = lst
    n_ext = sum(1 for x in lst if x["external"])
    print(f"{name}: nucleo con aparicion EXTERNA (gemelo) en {n_ext}/{len(lst)}")
    for x in lst:
        if x["external"]:
            print(f"   0x{x['vaddr']:08x} -> {[hex(h) for h in x['external']]}")

out = {"strings": recs, "twins": twins}
json.dump(out, open("analysis/s180_remote/pic_sites.json", "w"), indent=1)
print()
print("total pic sites:", sum(r["n_pic"] for r in recs))
print("cadenas con 0 sitios:", [hex(r["vaddr"]) for r in recs if r["n_pic"] == 0])
