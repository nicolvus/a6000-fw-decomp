#!/usr/bin/env python3
"""S156 — llamadas directas (BL) a un objetivo, con barrido tolerante a datos."""
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from common import BASE, B, N, U16, cstr  # noqa: E402

import capstone  # noqa: E402

MD = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
MD.detail = True


def bl_targets(lo, hi):
    """[(addr_de_la_BL, target)] de todas las BL de 32 bits Thumb en [lo,hi)."""
    out = []
    a = lo
    while a < hi:
        got = False
        for ins in MD.disasm(B[a - BASE:a - BASE + 4], a, count=1):
            if ins.mnemonic == "bl" and ins.op_str.startswith("#"):
                try:
                    out.append((ins.address, int(ins.op_str[1:], 0)))
                except ValueError:
                    pass
            got = True
            a += ins.size
            break
        if not got:
            a += 2
    return out


def callers(target, lo=BASE, hi=BASE + N):
    return [a for a, t in bl_targets(lo, hi) if t == target]


def context(addr, before=48, after=32):
    lo = max(BASE, addr - before)
    lines = []
    a = lo
    while a < addr + after:
        got = False
        for ins in MD.disasm(B[a - BASE:a - BASE + 4], a, count=1):
            mark = ">>" if ins.address == addr else "  "
            lines.append(f"{mark} {ins.address:#010x}  {ins.mnemonic:<8} {ins.op_str}")
            got = True
            a += ins.size
            break
        if not got:
            a += 2
    return "\n".join(lines)


if __name__ == "__main__":
    for t in sys.argv[1:]:
        tgt = int(t, 0)
        cs = callers(tgt)
        print(f"=== callers de {tgt:#x}: {len(cs)} ===")
        for c in cs:
            print(f"  {c:#x}")
