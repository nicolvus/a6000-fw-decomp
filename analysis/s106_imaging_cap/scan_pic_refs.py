#!/usr/bin/env python3
"""Escáner de referencias a cadenas en el firmware A6000 (esquema PIC Thumb).

En este firmware las cadenas no se apuntan con punteros absolutos. El código
hace, para cada cadena:

    ldr  rX, [pc, #inm]      ; carga del pool un desplazamiento W
    ...
    add  rX, pc              ; suma el PC ( Thumb: dirección de la instrucción + 4)

y el destino es `W + (dirección_del_add + 4)`. El `ldr` y el `add` pueden estar
separados por bastante código, así que se emparejan por **registro** y se
valida el emparejamiento exigiendo que el destino caiga **exactamente en el
inicio de una cadena** (conjunto de direcciones Validadas leyendo los bytes),
lo que hace vanishingmente improbable un falso positivo.

Uso:  python3 scan_pic_refs.py [LO HI]
Salida: analysis/s106_imaging_cap/pic_refs.json  (destino -> sitios)
"""
import bisect
import json
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
# Rango de cadenasconsidered "destino válido". Por defecto, toda la imagen: el
# rango 0x43c90000-0x43cd0000 que usaba la primera version solo cubria la zona
# de [IMAGING_CAP] y dejaba fuera modulos como [TRK] (0x43cebceb-0x43cfe31c).
STR_LO, STR_HI = 0x0, 0xFFFFFFFF
MAX_LDR_GAP = 4096          # ventana de emparejamiento ldr -> add

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def string_starts(lo, hi):
    """Direcciones de inicio de cadenas imprimibles en [lo, hi).

    Un inicio es un byte imprimible cuyo byte anterior **no** es imprimible
    (NUL o binario): así también se detectan cadenas que siguen a una tabla
    binaria (p. ej. los bytes 01 02 03 04 delante de "EnterCapturing").
    """
    o0, o1 = max(0, lo - BASE), min(N, hi - BASE)
    out = set()
    prev_print = False
    for i in range(o0, o1):
        c = B[i]
        cur = 32 <= c < 127
        if cur and not prev_print:
            out.add(BASE + i)
        prev_print = cur
    return out


def ldr_sites(lo, hi):
    """[(addr, reg, literal_value)] de los `ldr rX,[pc,#imm]`."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = U16(B, o)[0]
        lit = None
        reg = None
        if (h & 0xF800) == 0x4800:            # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:          # ldr.w rT, [pc, #imm12]
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, U32(B, o2)[0]))
    return out


def add_sites(lo, hi):
    """[(addr, reg)] de los `add rX, pc` de 16 bits."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400:
            rm = (h >> 3) & 0xF
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            if rm == 15:                      # Rm = PC
                out.append((a, rd))
    return out


def scan(lo, hi):
    starts = string_starts(STR_LO, STR_HI)
    ldrs = ldr_sites(lo, hi)
    adds = add_sites(lo, hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        # Se prueban TODOS los `ldr` del mismo registro dentro de la ventana (4 KB):
        # el `ldr` válido no siempre es el más cercano (el registro puede reutilizarse
        # entremedias). Solo se aceptan los destinos que caen en el inicio de una cadena.
        while i >= 0:
            la, w = v[i]
            if a - la > MAX_LDR_GAP:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if tgt in starts:
                out.setdefault(tgt, []).append(a)
            i -= 1
    return out


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else BASE
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else BASE + N
    dest = sys.argv[3] if len(sys.argv) > 3 else "analysis/s106_imaging_cap/pic_refs.json"
    res = scan(lo, hi)
    with open(dest, "w") as fh:
        json.dump({f"0x{k:x}": sorted(set(v)) for k, v in sorted(res.items())},
                  fh, indent=0)
    print(f"destinos en rango de cadenas: {len(res)}")
    print(f"escrito {dest}")


if __name__ == "__main__":
    sys.exit(main())
