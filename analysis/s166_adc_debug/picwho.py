#!/usr/bin/env python3
"""S166 — localiza los sitios que calculan una direccion PC-relativa (patron PIC: ldr [pc,#imm]
+ add rX,pc) y devuelve la direccion absoluta destino.

Uso: picwho.py 0xLO 0xHI
Salida: JSON {"destino": [sitios]} para los destinos en [LO,HI)
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
DATA = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()


def u32(a):
    o = a - BASE
    if 0 <= o and o + 4 <= len(DATA):
        return struct.unpack_from("<I", DATA, o)[0]
    return None


def main():
    lo, hi = int(sys.argv[1], 0), int(sys.argv[2], 0)
    out = {}
    n = len(DATA)
    i = 0
    while i < n - 4:
        h = struct.unpack_from("<H", DATA, i)[0]
        if (h >> 11) == 0b01001:          # ldr rX,[pc,#imm8]
            reg = (h >> 8) & 7
            imm = (h & 0xFF) * 4
            lit = ((i + 4) & ~3) + imm
            off = u32(lit)
            if off is None:
                i += 2
                continue
            # buscar el 'add rX,pc' mas cercano hacia adelante (mismo registro)
            j = i + 2
            while j < min(i + 80, n - 4):
                hj = struct.unpack_from("<H", DATA, j)[0]
                if (hj >> 11) == 0b10100 and (hj >> 8) & 7 == reg:
                    dst = (j + 4) + off
                    if lo <= dst < hi:
                        out.setdefault("%08x" % dst, []).append(BASE + j)
                    break
                j += 2
        i += 2
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
