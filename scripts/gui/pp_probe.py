#!/usr/bin/env python3
"""G34 — sonda en vivo del Picture Profile (telnet): cfg del núcleo (0x43EDF684+0x138…0x160), snapshot `pp` y caché de G33, copia de trabajo W.
Uso: A6000_HOST=IP pp_probe.py [segundos]  → imprime una línea cada vez que algo cambia. Solo lee."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import camera_silent as S

V = 0x40000000
CFG, SNAP, W = 0x43EDF684, 0x43FB7500, 0x43FB7EC0


def leer() -> dict:
    return {"cfg": S.rd(CFG + V + 0x138, 0x28), "pp": S.rd(SNAP + V, 16), "cache": S.rd(SNAP + V + 16, 24), "W0": S.rd(W + V, 16), "Wf": S.rd(W + V + 0xFF0, 16)}


if __name__ == "__main__":
    fin, ant = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 120), None
    while time.time() < fin:
        d = leer()
        if d != ant:
            print(time.strftime("%H:%M:%S"), d, flush=True)
            ant = d
        time.sleep(1)
