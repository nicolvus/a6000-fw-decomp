#!/usr/bin/env python3
"""S180 - desensamblado Thumb de un rango (capstone)."""
import sys
from capstone import *

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return "<fuera>"
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    ins = list(md.disasm(B[lo - BASE:hi - BASE], lo))
    for i in ins:
        extra = ""
        m = i.mnemonic
        if m in ("bl", "blx"):
            extra = f"  ; -> 0x{i.operands[0].imm:08x}"
        elif m in ("b", "b.w"):
            extra = f"  ; -> 0x{i.operands[0].imm:08x}"
        print(f"0x{i.address:08x}  {i.mnemonic:<8} {i.op_str}{extra}")


if __name__ == "__main__":
    main()
