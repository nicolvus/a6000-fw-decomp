#!/usr/bin/env python3
"""S156 — mapa función→cadena dentro de un rango de código, con la regla estricta."""
import bisect
import json
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from common import BASE, B, N, U16, U32, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402


def strict_sites(lo, hi):
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
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
        la, w = v[i]
        if a - la > 4096:
            continue
        out.append((a, (w + (a + 4)) & 0xFFFFFFFF, la))
    return out


def func_start(addr, back=0x8000):
    """Prólogo Thumb más cercano hacia atrás."""
    o = addr - BASE
    a = o - (o % 2)
    while a >= max(0, o - back):
        h1 = U16(B, a)[0]
        if (h1 & 0xFE00) == 0xB400 and (h1 & 0x00FF) != 0:
            return BASE + a
        if a + 4 <= N and h1 == 0xE92D:
            return BASE + a
        a -= 2
    return None


def strings_in(lo, hi):
    """[(addr_texto)] referenciados por PIC en [lo,hi) con la regla estricta."""
    out = []
    for a, tgt, la in strict_sites(lo, hi):
        s = cstr(tgt)
        if s and len(s) >= 2 and all(32 <= ord(c) < 127 for c in s):
            out.append((a, tgt, s))
    return out


if __name__ == "__main__":
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    for a, tgt, s in strings_in(lo, hi):
        print(f"{a:#x} -> {tgt:#x}  {s!r}")
