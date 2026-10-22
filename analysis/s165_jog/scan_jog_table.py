#!/usr/bin/env python3
"""S165 — tabla función→trazas del módulo [JOG] con la regla PIC estricta.

Los inicios de función se obtienen de: (a) destinos de BL dentro de la zona,
(b) ranuras de vtable (métodos virtuales), (c) prólogos `push {..,lr}` confirmados.
"""
import bisect
import json
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import BASE, B, N, U16, cstr, pic_ldr_sites, pic_add_sites  # noqa: E402
from scan_jog_bounds import bl_targets, push_lr_starts  # noqa: E402

REGION = (0x435ae400, 0x435afb00)

# vtables RTTI (vaddr de la ranura typeinfo -> clase)
VT = {
    0x43fbb5c0: "IllumiDev",
    0x43fbb5e0: "IllumiAd",
    0x43fbb600: "IllumiCam",
    0x43fbb620: "IllumiRPR0400",
    0x43fbb640: "JogDev",
    0x43fbb660: "JogFg",
    0x43fbb680: "JogTpu",
    0x43fbb6a0: "JogVGrip",
}


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


def main():
    lo, hi = REGION
    sites = strict_sites(lo, hi)
    cands = set()
    cands |= {a for a in bl_targets(lo, hi) if lo <= a < hi}
    cands |= {a & ~1 for a in push_lr_starts(lo, hi)}
    for a, cls in VT.items():
        for slot in range(8):
            v = int.from_bytes(B[a - BASE + 4 * slot:a - BASE + 4 * slot + 4], "little")
            if lo <= v < hi:
                cands.add(v & ~1)
    cands = sorted(cands)

    rows = []
    for a, dest, la in sites:
        s = cstr(dest)
        if not s:
            continue
        i = bisect.bisect_left(cands, a) - 1
        rows.append({"add": a, "dest": dest, "text": s,
                     "func": cands[i] if i >= 0 else None})
    for r in rows:
        mark = "***" if r["text"].startswith("[JOG]") else "   "
        fs = hex(r["func"]) if r["func"] is not None else "?"
        print(f"{mark} {fs:>12}  site={r['add']:#x}  dest={r['dest']:#x}  {r['text']!r}")
    json.dump({"candidates": cands, "sites": rows},
              open("analysis/s165_jog/jog_func_sites.json", "w"), indent=1)


if __name__ == "__main__":
    main()
