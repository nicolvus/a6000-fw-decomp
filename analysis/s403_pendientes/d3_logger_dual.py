#!/usr/bin/env python3
"""D3 (logger dual): por traza de S605–S627, ¿existe una segunda emisión estática hacia el logger global 0x43902718?

Criterio (el de S607/S611/S616): una referencia PIC al inicio de la cadena (ruta local) y otra a un punto interior de la misma
cadena, tras el prefijo, seguida de BL/B.W a 0x43902718 (ruta global), a <=0x300 B de la anterior. Resultado por ficha en
d3_logger_dual.json. Ausencia del patrón no refuta un logger dual con otra forma de código; solo deja de respaldarlo.
"""
import json
from pathlib import Path

import dual_scan
import pic

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name("d3_logger_dual.json")
VERIFIED = {"S607", "S611", "S616"}  # rutas ya contrastadas por instrucciones en analysis/verify_s6xx.py


def main() -> None:
    blob = pic.load("a6000")
    idx = dual_scan.index(pic.pic_refs(blob))
    sheets = {}
    for p in sorted((ROOT / "analysis").glob("s6[0-2][0-9]_*/*.json")):
        sid = p.parent.name[:4].upper()
        if not 605 <= int(sid[1:]) <= 627:
            continue
        d = json.loads(p.read_text())
        traces = []
        for t in d.get("trace_strings", []):
            lo, inner, du = dual_scan.trace_paths(blob, idx, int(t["vaddr"], 16), t["text"])
            traces.append({"vaddr": t["vaddr"], "ref_local": len(lo), "ref_interior": len(inner), "ruta_global": len(du)})
        n = len(traces)
        sheets[sid] = {
            "trazas": n,
            "con_ref_local": sum(1 for t in traces if t["ref_local"]),
            "con_ref_interior": sum(1 for t in traces if t["ref_interior"]),
            "con_ruta_global": sum(1 for t in traces if t["ruta_global"]),
            "estado": ("VERIFICADO_ESTATICO" if sid in VERIFIED else
                       "SIN_TRAZAS" if n == 0 else "NO_RESPALDADO_ESTATICO"),
            "detalle": traces,
        }
    OUT.write_text(json.dumps(sheets, indent=1) + "\n")
    for sid, s in sheets.items():
        print(sid, s["estado"], s["trazas"], s["con_ref_local"], s["con_ref_interior"], s["con_ruta_global"])


if __name__ == "__main__":
    main()
