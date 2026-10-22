#!/usr/bin/env python3
"""Desensamblado puntual (Capstone, Thumb) del firmware A6000 fw3.21.

Uso: .venv/bin/python analysis/s139_encseqctrl/dis.py 0x435d832c [n_insn] [--bytes]
"""
import os
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True


def dis(start, n=60, show_bytes=False):
    o = start - BASE
    out = []
    for i in md.disasm(B[o:o + n * 4], start):
        bts = B[i.address - BASE:i.address - BASE + i.size].hex()
        out.append(f"  0x{i.address:08x}: {bts:<10s} {i.mnemonic:<8s} {i.op_str}")
        if len(out) >= n:
            break
    return "\n".join(out)


if __name__ == "__main__":
    a = int(sys.argv[1], 0)
    n = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 60
    print(dis(a, n))
