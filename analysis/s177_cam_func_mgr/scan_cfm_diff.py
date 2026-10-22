#!/usr/bin/env python3
"""S177 — diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01 del módulo [CAM_FUNC_MGR].

Para cada una de las 43 cadenas de la A6000:
  - extrae el "núcleo" (lo que va tras `[CAM_FUNC_MGR]: `),
  - lo busca como subcadena en la A7S y en el A6300,
  - informa de la dirección donde aparece (si aparece).
Además busca marcadores del subsistema (LRBridge, "LR ...", Capcon) en los tres.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
FILES = {
    "A6000_fw321": "analysis/rea-independent/input/av-cam.bin",
    "A7S_fw320": ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                  "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "A6300_fw201": ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
B = {k: open(os.path.join(ROOT, v), "rb").read() for k, v in FILES.items()}

PRE = "[CAM_FUNC_MGR]: "
strings = json.load(open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_strings_raw.json")))
cads = strings["A6000_fw321"]["cadenas"]

MARKERS = [b"LRBridge", b"[LRB]", b"LR REQAPP", b"LR APP", b"LR VSC", b"LR V2 ",
           b"LR FSP", b"CapconEventQueue", b"CapconReply", b"capcon_api",
           b"Camcon", b"FunctionMessage", b"FunctionNotify", b"FunctionSetParam",
           b"tsk_capcon_sequence", b"tsk_rawdev_sequence"]

rows = []
for c in cads:
    txt = c["texto"]
    core = txt[len(PRE):] if txt.startswith(PRE) else txt
    row = {"vaddr": c["vaddr"], "texto": txt, "nucleo": core}
    for fw in ("A7S_fw320", "A6300_fw201"):
        hits = [m.start() for m in re.finditer(re.escape(core.encode()), B[fw])]
        row[fw] = [{"vaddr": hex(h + BASE)} for h in hits]
        row[fw + "_n"] = len(hits)
    rows.append(row)

tot = {"A7S_fw320": 0, "A6300_fw201": 0}
for r in rows:
    tot["A7S_fw320"] += 1 if r["A7S_fw320_n"] else 0
    tot["A6300_fw201"] += 1 if r["A6300_fw201_n"] else 0

mark = {}
for fw in FILES:
    mark[fw] = {m.decode("ascii"): len(re.findall(re.escape(m), B[fw])) for m in MARKERS}

res = {"filas": rows, "nucleos_encontrados": tot, "marcadores": mark}
json.dump(res, open(os.path.join(ROOT, "analysis/s177_cam_func_mgr/cfm_diff.json"), "w"),
          indent=1)

print(f"núcleos (texto tras el prefijo) hallados: A7S={tot['A7S_fw320']}/43  "
      f"A6300={tot['A6300_fw201']}/43\n")
for r in rows:
    print(f"{r['vaddr']}  A7S={r['A7S_fw320_n']}  A6300={r['A6300_fw201_n']}  "
          f"{r['nucleo'][:66]}")
print("\n--- marcadores ---")
for fw in FILES:
    print(fw, json.dumps(mark[fw], indent=1))
