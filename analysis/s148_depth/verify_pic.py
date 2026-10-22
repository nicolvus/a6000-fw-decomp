#!/usr/bin/env python3
"""S148 — verificacion manual de un par PIC (`ldr rX,[pc,#imm]` + `add rX,pc`).

Imprime, para cada sitio `add` dado:
  * el `ldr` emparejado (regla estricta: el mas cercano por detras, ventana 4 KB),
  * la direccion del literal pool y su valor,
  * el destino resuelto (W + add + 4) y la cadena a la que apunta,
  * los bytes crudos.

Uso:  .venv/bin/python analysis/s148_depth/verify_pic.py 0x435622ba 0x435627a6
"""
import bisect
import os
import struct
import sys

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from
MAX_LDR_GAP = 4096


def cstr(off, maxlen=120):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def all_ldrs():
    out = []
    for a in range(BASE, BASE + len(B) - 8, 2):
        o = a - BASE
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= len(B) - 4:
                out.append((a, reg, lit, U32(B, o2)[0]))
    return out


def main():
    ldrs = all_ldrs()
    by_reg = {}
    for a, reg, lit, w in ldrs:
        by_reg.setdefault(reg, []).append((a, lit, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    for arg in sys.argv[1:]:
        site = int(arg, 0)
        o = site - BASE
        h = U16(B, o)[0]
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            print(f"0x{site:08x}: no es `add rX,pc` (halfword=0x{h:04x})")
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg, [])
        i = bisect.bisect_right(keys[reg], site) - 1
        la, lit, w = v[i]
        tgt = (w + site + 4) & 0xFFFFFFFF
        print(f"add en 0x{site:08x}  reg=r{reg}")
        print(f"   ldr emparejado 0x{la:08x}  bytes={B[la-BASE:la-BASE+2].hex()}")
        print(f"   literal pool  0x{lit:08x} = 0x{w:08x}")
        print(f"   destino = 0x{w:08x} + 0x{site+4:08x} = 0x{tgt:08x}")
        print(f"   cadena: {cstr(tgt - BASE)!r}")
        print(f"   gap ldr->add = {site - la} B (limite {MAX_LDR_GAP})")


if __name__ == "__main__":
    main()
