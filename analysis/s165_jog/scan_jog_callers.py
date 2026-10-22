#!/usr/bin/env python3
"""S165 — llamantes globales (BL) de un conjunto de direcciones objetivo."""
import json
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U16  # noqa: E402


def all_bl_targets(lo, hi):
    """[(addr, target)] de todos los BL de la imagen en [lo,hi)."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0xF000:
            h2 = U16(B, o + 2)[0]
            if (h2 & 0xD000) == 0xD000:
                s = (h >> 10) & 1
                i1 = 1 - (((h >> 13) & 1) ^ s)
                i2 = 1 - (((h2 >> 11) & 1) ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
                if imm & 0x800000:
                    imm -= 1 << 25
                out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
                a += 4
                continue
            if (h2 & 0xD000) == 0x9000:
                a += 4
                continue
        a += 2
    return out


if __name__ == "__main__":
    targets = set(int(x, 0) for x in sys.argv[1:])
    lo = int(sys.argv[-3], 0) if False else BASE
    hi = BASE + N
    res = {t: [] for t in targets}
    for a, t in all_bl_targets(lo, hi):
        if t in res:
            res[t].append(a)
    for t in sorted(res):
        print(f"{t:#x} <- {[hex(x) for x in res[t]]}")
    json.dump({hex(t): res[t] for t in sorted(res)},
              open("analysis/s165_jog/jog_callers.json", "w"), indent=1)
