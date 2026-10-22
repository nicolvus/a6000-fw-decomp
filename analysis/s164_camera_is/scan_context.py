#!/usr/bin/env python3
"""S164 — contexto de cadenas referenciadas desde la region de codigo del modulo IS.

Uso: scan_context.py LO HI
Muestra todas las cadenas referenciadas (regla estricta, mapa global) desde sitios PIC
situados en [LO,HI), con la direccion del sitio y de la cadena.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
REFS = json.loads((ROOT / "analysis/s106_imaging_cap/pic_refs_strict_global.json").read_text())


def strings():
    out = {}
    for m in re.finditer(rb"[\x20-\x7e]{4,}", DATA):
        out[BASE + m.start()] = m.group().decode("latin1")
    return out


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    S = strings()
    filas = []
    for dest, sites in REFS.items():
        d = int(dest, 16)
        txt = S.get(d)
        if txt is None:
            continue
        for s in sites:
            if lo <= s < hi:
                filas.append((s, d, txt))
    filas.sort()
    for s, d, t in filas:
        print("site %08x  str %08x  %s" % (s, d, t))
    print("total", len(filas))


if __name__ == "__main__":
    main()
