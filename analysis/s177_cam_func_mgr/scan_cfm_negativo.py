#!/usr/bin/env python3
"""S177 — negativo acotado para la línea del obturador.

Comprueba la presencia de términos del obturador/exposición en:
  (a) las 43 cadenas [CAM_FUNC_MGR],
  (b) las 65 entradas de la tabla de funciones (origin + nombre),
  (c) las cadenas del bloque del módulo (0x43ca1242..0x43cb0400).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
B = open(os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin"), "rb").read()

TERMS = ["shutter", "silent", "curtain", "electro", "mech", "expos", "iso",
         "apert", "frame", "capture", "photo", "sensor", "compens", "read",
         "drv", "imager", "ob", "scan", "shut", "svd", "shd", "spl", "burst",
         "bracket", "interval", "movie", "still", "jpeg", "raw", "focus",
         "af ", "ae ", "exp", "zoom", "flash", "iso ", "white"]

cads = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_strings_raw.json")))
cads = cads["A6000_fw321"]["cadenas"]
ft = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_functable.json")))

grupos = {
    "43 cadenas [CAM_FUNC_MGR]": [c["texto"] for c in cads],
    "tabla de funciones (65)": [f"{e['origin'] or ''} {e['nombre']}"
                                for e in ft["entradas"]],
}
bloque = []
for m in re.finditer(rb"[\x20-\x7e]{4,}", B[0x43ca1242 - BASE:0x43cb0400 - BASE]):
    bloque.append(m.group().decode("ascii"))
grupos["bloque del módulo 0x43ca1242..0x43cb0400"] = bloque

res = {}
for g, textos in grupos.items():
    print(f"=== {g}  ({len(textos)} cadenas)")
    for t in TERMS:
        hits = [x for x in textos if t.lower() in x.lower()]
        if hits:
            print(f"   {t!r}: {len(hits)} -> {hits[:4]}")
    res[g] = {t: [x for x in textos if t.lower() in x.lower()] for t in TERMS}

json.dump(res, open(os.path.join(ROOT,
                                 "analysis/s177_cam_func_mgr/cfm_negativo.json"), "w"),
          indent=1)
