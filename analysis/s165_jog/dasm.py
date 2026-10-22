#!/usr/bin/env python3
"""S165 — desensamblado Thumb (toda la imagen es Thumb) con capstone."""
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N  # noqa: E402
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB  # noqa: E402

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = False


def disasm(lo, hi):
    """[(addr, texto)] — desensambla en modo Thumb desde `lo` (par)."""
    out = []
    a = lo & ~1
    while a < hi:
        o = a - BASE
        if o < 0 or o >= N:
            a += 2
            continue
        got = False
        for ins in md.disasm(B[o:o + 4], a, count=1):
            out.append((a, f"{ins.mnemonic} {ins.op_str}"))
            a += ins.size if ins.size else 2
            got = True
        if not got:
            a += 2
    return out


if __name__ == "__main__":
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    for a, txt in disasm(lo, hi):
        print(f"{a:#x}\t{txt}")
