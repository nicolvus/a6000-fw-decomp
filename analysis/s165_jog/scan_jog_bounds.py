#!/usr/bin/env python3
"""S165 — límites de función en el módulo [JOG]: destinos de BL + prólogos + vtables."""
import json
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U16, U32  # noqa: E402


def bl_targets(lo, hi):
    """Destinos de `bl`/`blx` inminutos en [lo,hi)."""
    out = set()
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xF800) == 0xF000:
            h2 = U16(B, o + 2)[0]
            if (h2 & 0xD000) == 0xD000:      # BL (32 bits)
                s = (h >> 10) & 1
                i1 = 1 - (((h >> 13) & 1) ^ s)
                i2 = 1 - (((h2 >> 11) & 1) ^ s)
                imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
                if imm & 0x800000:
                    imm -= 1 << 25
                out.add((a + 4 + imm) & 0xFFFFFFFF)
                a += 4
                continue
            if (h2 & 0xD000) == 0x9000:      # BLX (registro)
                a += 4
                continue
        a += 2
    return out


def push_lr_starts(lo, hi):
    out = set()
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x0100):     # push {rlist, lr}
            out.add(a)
        elif h == 0xE92D:                                # stmdb sp!, {.., lr}
            if U16(B, o + 2)[0] & 0x4000:
                out.add(a)
            a += 4
            continue
        a += 2
    return out


def pop_pc_ends(lo, hi):
    out = set()
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xBD00 and (h & 0x8000):     # pop {rlist, pc}
            out.add(a)
        elif h == 0xE8BD:                                # ldmia sp!, {.., pc}
            out.add(a)
            a += 4
            continue
        a += 2
    return out


if __name__ == "__main__":
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    bl = bl_targets(lo, hi)
    ps = push_lr_starts(lo, hi)
    pe = pop_pc_ends(lo, hi)
    inside = lambda s: sorted(x for x in s if lo <= x < hi)
    print("BL targets:", [hex(x) for x in inside(bl)])
    print("\npush{..lr}:", [hex(x) for x in inside(ps)])
    print("\npop{..pc}:", [hex(x) for x in inside(pe)])
    json.dump({"bl": inside(bl), "push": inside(ps), "pop": inside(pe)},
              open("analysis/s165_jog/jog_funcbounds.json", "w"), indent=1)
