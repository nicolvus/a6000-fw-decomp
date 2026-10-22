#!/usr/bin/env python3
"""S138 — busca ramas Thumb (`bl`, `b.w`, `blx`, `b` de 16 bits) que apunten a un destino.

Búsqueda **inversa** y rápida: se predecodifican todos los halfwords del binario y
para cada posición candidata se calculan los destinos posibles (las cuatro
combinaciones de los bits J1/J2, que ocupan los bits 22 y 23 del campo de offset).
Un resultado vacío es concluyente: ninguna rama de la imagen apunta al destino.

Nota: en este firmware las instrucciones Thumb-2 de 32 bits pueden estar en
direcciones ≡ 2 (mod 4) (p. ej. el `push.w` de 0x4379d83a documentado en el
proyecto), por lo que el barrido es de 2 en 2 bytes.

Salida: analysis/s138_camera_main_fc/fc_branches.json
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)
HW = struct.unpack("<%dH" % (N // 2), B[:N - (N % 2)])   # halfwords little-endian


def find(targets):
    """{objetivo: [(sitio, kind)]}"""
    tset = set(targets)
    out = {t: [] for t in targets}
    n = N // 2
    for i in range(n - 2):
        h1 = HW[i]
        if (h1 & 0xF800) == 0xE000:              # b T2 (16 bits)
            s = (h1 & 0x7FF) << 1
            if s & 0x400:
                s -= 0x800
            t = (BASE + 2 * i + 4 + s) & 0xFFFFFFFF
            if t in tset:
                out[t].append((BASE + 2 * i, "b16"))
            continue
        if (h1 & 0xF800) != 0xF000:              # no es rama de 32 bits
            continue
        h2 = HW[i + 1]
        if (h2 & 0xC000) not in (0xC000, 0x8000):
            continue
        base = ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if (h1 >> 10) & 1:                       # S = 1 -> offset negativo
            base -= 0x1000000
        a = BASE + 2 * i
        for jbits in (0, 0x400000, 0x800000, 0xC00000):
            t = (a + 4 + base + jbits) & 0xFFFFFFFF
            if t in tset:
                kind = {0xD000: "bl", 0x9000: "b.w", 0xC000: "blx",
                        0x8000: "b.w?"}.get(h2 & 0xD000, "b?")
                out[t].append((a, kind))
    return out


def main():
    targets = [int(x, 16) for x in sys.argv[1:]]
    res = find(targets)
    for t in targets:
        print(f"0x{t:x}: {len(res[t])} ramas -> {[(k, hex(a)) for a, k in res[t]]}")
    json.dump({f"0x{t:x}": [{"site": f"0x{a:x}", "kind": k} for a, k in res[t]]
               for t in targets},
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_branches.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
