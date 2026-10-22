#!/usr/bin/env python3
"""S177 — comprueba la hipótesis "el prefijo `[CAM_FUNC_MGR]: ` (16 B) se insertó
delante del literal original, y la llamada de log antigua sigue apuntando a +16".

Para cada una de las 43 cadenas:
  - comprueba que B[vaddr+16 : ] empieza por el texto sin el prefijo,
  - comprueba que el texto sin prefijo aparece en la A7S y en el A6300,
  - comprueba que en la A7S la cadena sin prefijo ocupa la MISMA posición
    relativa dentro del bloque (offset = vaddr - base_bloque).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
B = {k: open(os.path.join(ROOT, v), "rb").read() for k, v in FILES.items()}
PRE = b"[CAM_FUNC_MGR]: "

cads = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_strings_raw.json")))
cads = cads["A6000_fw321"]["cadenas"]

rows = []
n_gem = 0
for c in cads:
    va = int(c["vaddr"], 16)
    o = va - BASE
    txt = c["texto"].encode()
    core = c["texto"][len(PRE):].encode()
    gem = B["A6000"][o + len(PRE):o + len(PRE) + len(core)] == core
    row = {"vaddr": c["vaddr"], "texto": c["texto"], "core": c["texto"][len(PRE):],
           "gemelo_mas16": gem, "long_prefijo": len(PRE)}
    for fw in ("A7S", "A6300"):
        hits = [m.start() for m in re.finditer(re.escape(core), B[fw])]
        row[fw + "_n"] = len(hits)
        row[fw + "_vaddr"] = [hex(h + BASE) for h in hits]
        if hits:
            row[fw + "_texto"] = B[fw][hits[0]:B[fw].find(b"\x00", hits[0])].decode(
                "ascii", "replace")
    n_gem += bool(gem)
    rows.append(row)

out = {"prefijo_bytes": len(PRE), "n_cadenas": len(cads), "n_gemelo_mas16": n_gem,
       "filas": rows}
json.dump(out, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_prefijo.json"), "w"),
          indent=1)
print(f"prefijo = {len(PRE)} B   cadenas = {len(cads)}   "
      f"con gemelo exacto en +{len(PRE)}: {n_gem}")
for r in rows:
    print(f"{r['vaddr']} gemelo+16={r['gemelo_mas16']}  A7S={r['A7S_n']}@"
          f"{r.get('A7S_vaddr')}  A6300={r['A6300_n']}@{r.get('A6300_vaddr')}  "
          f"{r['core'][:52]}")
    if "A7S_texto" in r:
        assert r["A7S_texto"].endswith(r["core"]), r
