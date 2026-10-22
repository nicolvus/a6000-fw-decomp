#!/usr/bin/env python3
"""S123 — IDs de parámetro (`movw rX, #0x94xx`) que usa el control de captura.

En este firmware los "parámetros" compartidos (ImageParam_Capture, DMM, recursos)
se obtienen con `bl getParam(id, &out)`, y el id se carga con `movw r1, #0x94xx`.
Este script lista esos ids y en qué función aparecen, dentro de las regiones de
código del módulo `[CAMERA_MAIN_CC]`.

Uso:  param_ids.py
"""
import json
import os
import struct
from collections import defaultdict

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

# (nombre, inicio, fin) de las regiones de código del módulo CC
REGIONS = [
    ("cc-methods", 0x4379ec84, 0x4379fc10),
    ("cc-lut", 0x437a1a7e, 0x437a27c0),
    ("cc-ie", 0x437a6890, 0x437a80b0),
    ("cc-miniraw", 0x437a8fac, 0x437a9560),
    ("cc-makernote", 0x437ada6e, 0x437adb80),
    ("cc-camcore-3dlut", 0x4381d296, 0x4381d390),
    ("cc-stages", 0x43aeb2ae, 0x43aeb650),
    ("cc-helpers", 0x437a0cfc, 0x437a1a7e),
    ("cc-obj", 0x437ad500, 0x437ae000),
]


def main():
    data = open(BIN, "rb").read()
    rows = []
    for name, lo, hi in REGIONS:
        fh = open(BIN, "rb")
        fh.seek(lo - BASE)
        code = fh.read(hi - lo)
        fh.close()
        for ins in md.disasm(code, lo):
            if ins.mnemonic == "movw" and "#" in ins.op_str:
                try:
                    v = int(ins.op_str.split("#")[1], 0)
                except ValueError:
                    continue
                rows.append({"region": name, "addr": f"0x{ins.address:x}",
                             "insn": f"{ins.mnemonic} {ins.op_str}", "imm": v})
    json.dump({"module": "CAMERA_MAIN_CC", "movw": rows},
              open(os.path.join(HERE, "param_ids.json"), "w"), indent=1, ensure_ascii=False)
    groups = defaultdict(list)
    for r in rows:
        groups[r["imm"]].append(r)
    for v in sorted(groups):
        rs = groups[v]
        print(f"0x{v:04x}  n={len(rs):2d}  regiones={sorted({r['region'] for r in rs})}")


if __name__ == "__main__":
    main()
