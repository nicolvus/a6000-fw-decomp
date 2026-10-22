#!/usr/bin/env python3
"""S122 — referencias PIC **dirigidas** a las 127 trazas `[CAMERA_MAIN_TC]`.

Diferencia con `scan_pic_refs_strict.py`: éste filtra destinos que sean *inicio de cadena*.
Aquí el destino puede ser cualquier dirección dentro del conjunto objetivo, porque hay
trazas cuyo prefijo `[CAMERA_MAIN_TC]` NO es inicio de cadena (va pegado a bytes imprimibles
previos) y porque el código usa **dos punteros** por traza: la cadena completa (con prefijo)
y el texto interior (sin prefijo).

Regla de emparejamiento: **estricta** (canónica del repo) — cada `add rX,pc` se empareja con
el `ldr rX,[pc,#imm]` más cercano por detrás, mismo registro, ventana 4 KB.

Uso: scan_refs_targeted.py [RUTA_SALIDA]
"""
import bisect
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
CODE_LO, CODE_HI = 0x43541000, 0x43C90000
MAX_GAP = 4096
PREFIX = b"[CAMERA_MAIN_TC]"

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from


def targets():
    """{vaddr: (indice, tipo)} para prefijo, inicio de cadena y texto interior."""
    out = {}
    idx = 0
    start = 0
    while True:
        i = B.find(PREFIX, start)
        if i < 0:
            break
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        inner = i + len(PREFIX)
        while inner < N and B[inner] in (0x20, 0x3A):
            inner += 1
        for v, kind in ((BASE + i, "prefix"), (BASE + s, "string"),
                        (BASE + inner, "inner")):
            out[v] = (idx, kind)
        idx += 1
        start = i + 1
    return out


def main():
    tg = targets()
    last = {}   # reg -> (addr, W) del `ldr rX,[pc,#imm]` más reciente
    results = []
    a = CODE_LO
    while a < CODE_HI:
        o = a - BASE
        if o < 0 or o > N - 8:
            break
        h = U16(B, o)[0]
        reg = None
        if (h & 0xF800) == 0x4800:                       # ldr rT,[pc,#imm5*4]
            reg = (h >> 8) & 7
            pool = ((a + 4) & ~3) + (h & 0xFF) * 4
        elif (h & 0xFF7F) == 0xF85F:                     # ldr.w rT,[pc,#imm12]
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            pool = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= pool - BASE <= N - 4:
            last[reg] = (a, U32(B, pool - BASE)[0])
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:   # add rX, pc (16 bits)
            d = ((h >> 7) & 1) << 3 | (h & 7)
            if d in last and (a - last[d][0]) <= MAX_GAP:
                dest = (last[d][1] + a + 4) & 0xFFFFFFFF
                if dest in tg:
                    results.append({"add": f"0x{a:x}", "ldr": f"0x{last[d][0]:x}",
                                    "reg": f"r{d}", "dest": f"0x{dest:x}",
                                    "idx": tg[dest][0], "kind": tg[dest][1]})
        a += 2
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "refs_targeted.json")
    json.dump({"rule": "strict", "n": len(results), "hits": results},
              open(out, "w"), indent=1)
    print("pares:", len(results), "->", out)


if __name__ == "__main__":
    main()
