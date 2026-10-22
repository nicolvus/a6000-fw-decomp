#!/usr/bin/env python3
"""S120 — desensamblador Thumb mínimo (para verificar sitios y estructuras).

Uso:  disasm_thumb.py VADDR [N_INSTR] [RUTA_BIN]
Convención: vaddr = 0x43541000 + file_offset.
"""
import os
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")


def disasm(vaddr, n=200, path=BIN, length=None):
    data = open(path, "rb").read()
    off = vaddr - BASE
    length = length or n * 4
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    out = []
    for ins in md.disasm(data[off:off + length], vaddr):
        out.append(ins)
        if len(out) >= n:
            break
    return out


def main():
    vaddr = int(sys.argv[1], 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    path = sys.argv[3] if len(sys.argv) > 3 else BIN
    for ins in disasm(vaddr, n, path):
        print(f"0x{ins.address:08x}:  {ins.bytes.hex():<12} {ins.mnemonic:<10} {ins.op_str}")


if __name__ == "__main__":
    main()
