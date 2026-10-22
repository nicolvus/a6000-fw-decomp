#!/usr/bin/env python3
"""S119 — desensamblado anotado del codigo del modulo `[APL]`.

Resuelve, para cada `add rX, pc`, las cadenas destino del esquema PIC:
  - "estricto": el `ldr` del mismo registro mas cercano por debajo (4 KB)
  - "canonico": todos los `ldr` del mismo registro en 4 KB (regla del repo)

Uso: python3 annotate_code.py LO HI [etiqueta]
"""
import bisect
import json
import os
import struct
import sys

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
MAX_GAP = 4096

B = open(BIN, "rb").read()


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    if e == o:
        return None
    return B[o:e].decode("latin1")


def pool_entries(lo, hi):
    """Para cada instruccion `ldr rX,[pc,#imm]`: (addr, reg, literal_addr, valor)."""
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 8:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= len(B) - 4:
            out.append((a, reg, lit, struct.unpack_from("<I", B, o2)[0]))
    return out


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    ldrs = pool_entries(lo - 0x4000, hi)
    by_reg = {}
    for a, reg, lit, val in ldrs:
        by_reg.setdefault(reg, []).append((a, val))
    for v in by_reg.values():
        v.sort()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    o = lo - BASE
    print(f"===== {tag} {lo:#x}-{hi:#x}")
    for i in md.disasm(B[o:hi - BASE], lo):
        ann = ""
        if len(i.bytes) == 2 and i.bytes[1] == 0x44:
            h = struct.unpack_from("<H", i.bytes, 0)[0]
            rd = (((h >> 7) & 1) << 3) | (h & 7)
            if ((h >> 3) & 0xF) != 15:
                rd = None
        else:
            rd = None
        if rd is not None:
            cand = by_reg.get(rd, [])
            if cand:
                idx = bisect.bisect_right([c[0] for c in cand], i.address) - 1
                if idx >= 0 and i.address - cand[idx][0] <= MAX_GAP:
                    strict = (cand[idx][1] + i.address + 4) & 0xFFFFFFFF
                    s = cstr(strict)
                    allv = []
                    for la, val in cand:
                        if i.address - la > MAX_GAP or la > i.address:
                            continue
                        d = (val + i.address + 4) & 0xFFFFFFFF
                        t = cstr(d)
                        if t:
                            allv.append((la, d, t))
                    ann = f"  ; STRICT {strict:#x} {s!r}"
                    if len(allv) > 1:
                        ann += " || CANON " + " ; ".join(
                            f"{d:#x} {t!r}" for _, d, t in allv)
        print(f"{i.address:#x}  {i.bytes.hex():<12} {i.mnemonic:<8} {i.op_str}{ann}")


if __name__ == "__main__":
    main()
