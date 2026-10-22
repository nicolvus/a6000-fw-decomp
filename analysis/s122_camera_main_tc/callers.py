#!/usr/bin/env python3
"""S122 — buscador de llamadores (`bl` / `blx` inmediato) por decodificación de halfwords.

No desensambla la imagen completa: decodifica el par de halfwords de `BL` (T1) y de
`BLX imm` (T2) en cada offset par y resuelve el destino. Los falsos positivos por datos
son ~2^-24 por offset; todo sitio reportado se verifica luego con Capstone (`disasm.py`).

Uso: callers.py <vaddr_destino> [binario]
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def bl_sites(data, lo, hi):
    U16 = struct.Struct("<H").unpack_from
    a = lo
    while a < hi - 4:
        o = a - BASE
        h1 = U16(data, o)[0]
        h2 = U16(data, o + 2)[0]
        if (h1 & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000:
            s = (h1 >> 10) & 1
            j1 = (h2 >> 13) & 1
            j2 = (h2 >> 11) & 1
            i1 = 1 - (j1 ^ s)
            i2 = 1 - (j2 ^ s)
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | \
                  ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
            if s:
                imm -= 1 << 25
            yield a, (a + 4 + imm) & 0xFFFFFFFF
        a += 2


def main():
    target = int(sys.argv[1], 0)
    path = sys.argv[2] if len(sys.argv) > 2 else BIN
    data = open(path, "rb").read()
    hits = [hex(a) for a, t in bl_sites(data, BASE, BASE + len(data)) if t == target]
    print(f"destino 0x{target:x}: {len(hits)} sitios")
    for h in hits:
        print(" ", h)


if __name__ == "__main__":
    main()
