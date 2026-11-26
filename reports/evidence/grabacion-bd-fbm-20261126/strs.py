#!/usr/bin/env python3
"""Lista cadenas y simbolos referenciados por un rango de codigo Thumb."""
import sys

sys.path.insert(0, "reports/evidence/fbm-sector31-consola-20261126/evidencia")
import mprdis as M
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def scan(lo, hi):
    va = lo
    seen = []
    while va < hi:
        b = M.rd(va, 4)
        ins = next(md.disasm(b, va), None)
        if not ins:
            va += 2
            continue
        if ins.mnemonic == "ldr" and "[pc," in ins.op_str:
            try:
                imm = int(ins.op_str.split("#")[-1].rstrip("]"), 0)
            except ValueError:
                imm = None
            if imm is not None:
                pool = ((ins.address + 4) & ~3) + imm
                v = M.rd32(pool)
                if v:
                    s = M.cstr(v)
                    if s:
                        seen.append((ins.address, hex(v), s))
        va += ins.size or 2
    return seen


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if ":" in arg:
            a, n = arg.split(":")
            lo, hi = int(a, 0), int(a, 0) + int(n, 0)
        else:
            lo = int(arg, 0)
            hi = lo + 0x400
        print(f"--- {lo:#x}..{hi:#x}")
        for at, v, s in scan(lo, hi):
            print(f"{at:#x} {v:>10} {s!r}")
