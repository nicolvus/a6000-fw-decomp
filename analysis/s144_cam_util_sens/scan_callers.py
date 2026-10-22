#!/usr/bin/env python3
"""S144 — localizadores de referencias a funciones (llamadas `bl`/`blx` y
punteros absolutos de 4 B) en la imagen A6000 fw3.21.

No usa REA/Ghidra: solo bytes.

  * `bl`/`b.w`/`blx` (inmediato): decodifica todas las instrucciones de
    transferencia de control de 16 y 32 bits y devuelve las que apuntan a
    un destino dado.
  * punteros absolutos: busca el valor de 4 B (con el bit Thumb) en toda la
    imagen y devuelve sus posiciones.

Convencion: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from


def sign_ext(v, bits):
    m = 1 << (bits - 1)
    return (v ^ m) - m


def branch_targets(lo, hi):
    """[(addr, kind, target)] de todas las BL/B.W/BLX-inmediato en [lo,hi)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h1 = U16(B, o)[0]
        if (h1 & 0xF800) == 0xE000:              # BL de 16 bits
            imm = sign_ext(h1 & 0x7FF, 11) << 1
            out.append((a, "bl16", (a + 4 + imm) & 0xFFFFFFFF))
            a += 2
            continue
        if (h1 & 0xF800) == 0xF000:              # Thumb-2 de 32 bits
            h2 = U16(B, o + 2)[0]
            S = (h1 >> 10) & 1
            if (h2 & 0xC000) == 0xC000:          # 11 J1 x J2 ...
                if h2 & 0x1000:                  # BL (imm24)
                    imm10 = h1 & 0x3FF
                    J1 = (h2 >> 13) & 1
                    J2 = (h2 >> 11) & 1
                    imm11 = h2 & 0x7FF
                    I1 = 1 - (J1 ^ S)
                    I2 = 1 - (J2 ^ S)
                    imm = (S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1)
                    out.append((a, "bl", (a + 4 + sign_ext(imm, 25)) & 0xFFFFFFFF))
                    a += 4
                    continue
            elif (h2 & 0xC000) == 0x8000:        # 10 J1 0 J2 ...
                if h2 & 0x2000:                  # B.W (imm21)
                    imm10 = h1 & 0x3FF
                    J1 = (h2 >> 13) & 1
                    J2 = (h2 >> 11) & 1
                    imm11 = h2 & 0x7FF
                    I1 = 1 - (J1 ^ S)
                    I2 = 1 - (J2 ^ S)
                    imm = (S << 20) | (I1 << 19) | (I2 << 18) | (imm10 << 10) | (imm11 << 1)
                    out.append((a, "b.w", (a + 4 + sign_ext(imm, 21)) & 0xFFFFFFFF))
                    a += 4
                    continue
        a += 2
    return out


def absolute_ptrs(value):
    """posiciones (vaddr) donde aparece el u32 `value`."""
    pat = struct.pack("<I", value & 0xFFFFFFFF)
    out = []
    i = 0
    while True:
        j = B.find(pat, i)
        if j < 0:
            break
        out.append(BASE + j)
        i = j + 1
    return out


def main():
    targets = [int(x, 0) for x in sys.argv[1:]]
    branches = branch_targets(BASE, BASE + N)
    res = {}
    for t in targets:
        calls = [(a, k) for a, k, tg in branches if tg == t]
        ptrs = absolute_ptrs(t | 1)
        res[f"0x{t:08x}"] = {
            "llamadas_bl": [{"site": f"0x{a:08x}", "tipo": k} for a, k in calls],
            "punteros_absolutos": [f"0x{p:08x}" for p in ptrs],
        }
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
