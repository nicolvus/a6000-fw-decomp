#!/usr/bin/env python3
"""S177 — referencias PIC (regla estricta) a las 43 cadenas [CAM_FUNC_MGR].

Usa el mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json` (ya
calculado, no se re-barea la imagen) y, para comprobación, un escaneo local con
la MISMA regla sobre la zona de código donde caen los sitios.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")
STRINGS = os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_strings_raw.json")
OUT = os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_pic_sites.json")

g = json.load(open(GLOBAL))
s = json.load(open(STRINGS))
cads = s["A6000_fw321"]["cadenas"]

res = {"cadenas": [], "n_cadenas": len(cads)}
n_sitios = 0
muertas = []
for c in cads:
    key = c["vaddr"]
    sites = [hex(a) for a in g.get(key, [])]
    res["cadenas"].append({"vaddr": key, "texto": c["texto"], "sitios": sites,
                           "n_sitios": len(sites)})
    n_sitios += len(sites)
    if not sites:
        muertas.append(key)

res["n_sitios_total"] = n_sitios
res["n_muertas"] = len(muertas)
res["muertas"] = muertas
res["n_funciones"] = None
json.dump(res, open(OUT, "w"), indent=1)
print(f"cadenas: {len(cads)}  sitios: {n_sitios}  muertas: {len(muertas)}")
for c in res["cadenas"]:
    print(f"  {c['vaddr']}  n={c['n_sitios']}  {c['texto'][:70]}")
