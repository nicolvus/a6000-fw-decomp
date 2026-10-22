#!/usr/bin/env python3
"""S138 — mapa función→traza de `[CAMERA_MAIN_FC]` con la regla canónica (estricta).

Usa el mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json` (regla
estricta: cada `add rX,pc` con el `ldr rX,[pc]` más cercano) y, opcionalmente,
recalcula los sitios con `scan_pic_refs_strict.py` para un rango acotado.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")

# sub-bloque de código plausible: los emisores de CAMERA_MAIN_* rondan 0x4354xxxx-0x439cxxxx
CODE_LO, CODE_HI = 0x43541000, 0x43A00000


def load_strings():
    p = os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_strings.json")
    d = json.load(open(p))
    return d["a6000"]["items"]


def func_of(addr):
    """Función envolvente: usa la tabla de funciones si existe, si no acota por bloques."""
    return addr


def main():
    items = load_strings()
    g = json.load(open(GLOBAL))
    out = {}
    for it in items:
        key = f"0x{it['vaddr']:x}"
        sites = g.get(key, [])
        out[key] = {"text": it["text"], "sites": sites, "n_sites": len(sites)}
        print(f"{key}  sitios={len(sites)}  {it['text'][:90]!r}")
        for s in sites:
            print(f"     sitio 0x{s:x}")
    dest = os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_pic_refs.json")
    json.dump(out, open(dest, "w"), indent=1)
    print("->", dest)


if __name__ == "__main__":
    main()
