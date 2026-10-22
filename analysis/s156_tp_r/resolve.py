#!/usr/bin/env python3
"""S156 — resuelve literales PIC (ldr rX,[pc,#imm] + add rX,pc) a direcciones absolutas.

Uso:  resolve.py LO HI [solo_no_cadena]
"""
import bisect
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from common import BASE, B, N, U16, U32, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402


def resolve_range(lo, hi):
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = []
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        if i < 0:
            continue
        la, w, lit = v[i]
        if a - la > 4096:
            continue
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        out.append((a, la, lit, tgt))
    return out


if __name__ == "__main__":
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    only_str = "--str" in sys.argv
    for a, la, lit, tgt in resolve_range(lo, hi):
        s = cstr(tgt)
        if only_str and not s:
            continue
        print(f"{a:#x} (ldr {la:#x} pool {lit:#x}) -> {tgt:#x}  {s!r}")
