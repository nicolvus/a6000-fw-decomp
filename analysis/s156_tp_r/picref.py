#!/usr/bin/env python3
"""S156 — utilidades de referencias PIC (método canónico: ldr+add)."""
import bisect
import sys

sys.path.insert(0, "analysis/s156_tp_r")
from common import BASE, B, N, U16, U32, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402


def build(lo=BASE, hi=BASE + N):
    ldrs = pic_ldr_sites(lo, hi)
    adds = pic_add_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    return ldrs, adds, by_reg, keys


def refs_to(target, ldrs, adds, by_reg, keys, window=4096):
    """Sitios que pueden referencia `target` por el esquema ldr/add.

    Devuelve (add_addr, ldr_addr, reg, strict).
    """
    out = []
    add_by_addr = {a: reg for a, reg in adds}
    for la, reg, w, lit in ldrs:
        a = (target - w - 4) & 0xFFFFFFFF
        if add_by_addr.get(a) != reg:
            continue
        if not (la < a <= la + window):
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        nearest = by_reg[reg][i][0] if i >= 0 else None
        out.append((a, la, reg, nearest == la))
    return sorted(set(out))


def strict_map(lo=BASE, hi=BASE + N):
    """Mapa destino -> [add_addr] con la regla estricta."""
    ldrs, adds, by_reg, keys = build(lo, hi)
    out = {}
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
        tgt = (w + (a + 4)) & 0xFFFFFFFF
        out.setdefault(tgt, []).append(a)
    return {k: sorted(set(v)) for k, v in out.items()}
