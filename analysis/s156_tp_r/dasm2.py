#!/usr/bin/env python3
"""S156 — desensamblador mínimo (Thumb) parametrizable.

Uso:  dasm2.py LO HI [A6000|A7S|A6300]
"""
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from diffscan import BASE, FILES  # noqa: E402

import capstone  # noqa: E402


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    which = sys.argv[3] if len(sys.argv) > 3 else "A6000"
    B = open(FILES[which], "rb").read()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    a = lo
    while a < hi:
        got = False
        for ins in md.disasm(B[a - BASE:a - BASE + 4], a, count=1):
            print(f"{ins.address:#010x}  {ins.bytes.hex():<12} {ins.mnemonic:<8} {ins.op_str}")
            got = True
            a += ins.size
            break
        if not got:
            a += 2


if __name__ == "__main__":
    main()
