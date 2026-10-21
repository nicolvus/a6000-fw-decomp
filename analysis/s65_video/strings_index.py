#!/usr/bin/env python3
"""Índice local de cadenas ASCII de av-cam.bin con dirección virtual (base 0x43541000).
Uso: strings_index.py [patrón ...]  -> imprime "ADDR<TAB>offset<TAB>cadena"
Sin patrones: vuelca todas a stdout (grande)."""
import sys, re

BASE = 0x43541000
PATH = "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin"
data = open(PATH, "rb").read()
# runs de ASCII imprimible >=4
pat = re.compile(rb"[\x20-\x7e]{4,}")
rows = []
for m in pat.finditer(data):
    off = m.start()
    rows.append((BASE + off, off, m.group().decode("ascii", "replace")))
rows.sort()
if len(sys.argv) > 1:
    pats = [p.lower() for p in sys.argv[1:]]
    for addr, off, s in rows:
        low = s.lower()
        if any(p in low for p in pats):
            print(f"0x{addr:08x}\t0x{off:x}\t{s}")
else:
    for addr, off, s in rows:
        print(f"0x{addr:08x}\t0x{off:x}\t{s}")
