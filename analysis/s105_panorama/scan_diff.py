#!/usr/bin/env python3
"""S105 — diferencial normalizado de cadenas panorama/sweep/interval A6000 vs A7S.

Normaliza: quita el prefijo de módulo "[IMAGING]: "/"[IMAGING_CAP]: " y el sufijo
" : %s:%d" (fichero:línea) para comparar el *contenido* del mensaje.
Convención: vaddr = 0x43541000 + off en AMBOS blobs.
"""
import re, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
BLOBS = {"A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
         "A7S": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")}
PAT = re.compile(rb"[\x20-\x7e]{4,}")
KEYS = ["panorama", "Panorama", "PANORAMA", "sweep", "Sweep", "SWEEP",
        "stitch", "Stitch", "interval", "Interval", "INTERVAL",
        "Bracket", "bracket", "BRACKET", "BracketAF"]

def norm(t):
    for p in ("[IMAGING]: ", "[IMAGING_CAP]: ", "[CAMERA_MAIN_YC]: ", "[CAMERA_MAIN_TC]: "):
        if t.startswith(p):
            t = t[len(p):]
    t = re.sub(r"\s*:\s*%s:%d$", "", t)
    return t

def sel(which):
    data = BLOBS[which].read_bytes()
    out = []
    for m in PAT.finditer(data):
        t = m.group(0).decode("latin-1")
        if any(k in t for k in KEYS):
            out.append((m.start() + BASE, m.start(), t))
    return out

A, B = sel("A6000"), sel("A7S")
na = {}
for v, o, t in A:
    na.setdefault(norm(t), (v, o, t))
nb = {}
for v, o, t in B:
    nb.setdefault(norm(t), (v, o, t))
print(f"# A6000: {len(A)} ocurrencias / {len(na)} mensajes normalizados")
print(f"# A7S  : {len(B)} ocurrencias / {len(nb)} mensajes normalizados")
print("\n## Solo A6000:")
for k in sorted(set(na) - set(nb)):
    v, o, t = na[k]
    print(f"  0x{v:08x} off=0x{o:08x} | {t}")
print("\n## Solo A7S:")
for k in sorted(set(nb) - set(na)):
    v, o, t = nb[k]
    print(f"  0x{v:08x} off=0x{o:08x} | {t}")
print(f"\n## Comunes: {len(set(na) & set(nb))}")
