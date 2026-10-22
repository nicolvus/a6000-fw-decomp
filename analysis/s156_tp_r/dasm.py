#!/usr/bin/env python3
"""Desensamblador mínimo (Thumb) para el hito S156 — módulo [TP_R].

Uso:  dasm.py LO HI [BASE_VADDR]
Por defecto usa el binario de la A6000 fw3.21 y BASE=0x43541000.
Continúa tras instrucciones inválidas (saltando 2 bytes) para no perder
el resto de la región.
"""
import sys

import capstone

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    base = int(sys.argv[3], 0) if len(sys.argv) > 3 else BASE
    path = BIN
    b = open(path, "rb").read()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    a = lo
    while a < hi:
        o = a - base
        chunk = b[o:o + 2]
        if len(chunk) < 2:
            break
        got = False
        for ins in md.disasm(b[o:o + 4], a, count=1):
            print(f"{ins.address:#010x}  {ins.bytes.hex():<12} {ins.mnemonic:<8} {ins.op_str}")
            got = True
            a += ins.size
            break
        if not got:
            print(f"{a:#010x}  {'??':<12} .word   0x{int.from_bytes(chunk,'little'):08x}")
            a += 2


if __name__ == "__main__":
    main()
