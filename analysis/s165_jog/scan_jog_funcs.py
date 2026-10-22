#!/usr/bin/env python3
"""S165 — mapa función→traza [JOG] con la regla PIC estricta (canónica S106)."""
import bisect
import json
import sys

sys.path.insert(0, "analysis/s165_jog")
from common import (BASE, B, N, U16, U32, cstr, pic_ldr_sites, pic_add_sites,
                    func_starts)  # noqa: E402

JOG = {  # destino → texto (las 14 trazas [JOG])
    0x43c40eb4: "[JOG]JogMain::%s:%d",
    0x43c40ef2: "[JOG]ERR. osal_try_valloc_msg. err=0x%x, line=%d",
    0x43c40f23: "[JOG]<Send Event> key_code = 0x%x, deg/sec = %d",
    0x43c40f53: "[JOG]ERR. osal_snd_msg. err=0x%x, line=%d",
    0x43c40f85: "[JOG]ERR. osal_free_timer. err=0x%x, line=%d",
    0x43c40fb2: "[JOG]JogFg::%s:%d",
    0x43c40fc4: "[JOG]ERR. osal_alloc_timer. err=0x%x, line=%d",
    0x43c40ff2: "[JOG]ERR. osal_set_timer. err=0x%x, line=%d",
    0x43c410a2: "[JOG]JogTpu::%s:%d",
    0x43c410fe: "[JOG]JogVGrip::%s:%d",
    0x43c41113: "[JOG]UpdateDataFromVgrip SndErr, line=%d",
    0x43c41184: "[JOG]JogKey::%s:%d:0x%x,%d",
    0x43c4119f: "[JOG]JogKey::%s:%d,pos:%d->%d",
    0x43c411bd: "[JOG]JogKey::%s:%d,Deg=0,Not Send",
}


def strict_sites(lo, hi):
    """[(addr_add, destino)] con la regla estricta (ldr más cercano del mismo registro)."""
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
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x435ad000
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x435b0800
    sites = strict_sites(lo, hi)
    starts = [a for a, _ in func_starts(lo, hi)]
    keys = list(starts)

    rows = []
    for a, tgt, la in sites:
        s = cstr(tgt)
        if s is None:
            continue
        i = bisect.bisect_left(keys, a) - 1
        fstart = keys[i] if i >= 0 else None
        rows.append({"add": a, "ldr": la, "dest": tgt, "text": s,
                     "func": fstart, "is_jog": tgt in JOG})

    for r in rows:
        if r["is_jog"]:
            print(f"{r['add']:#x}  ldr={r['ldr']:#x}  -> {r['dest']:#x}  {r['text']!r}  func~{r['func'] and hex(r['func'])}")

    json.dump(rows, open("analysis/s165_jog/jog_pic_sites.json", "w"), indent=1)
    print(f"\n{len(rows)} sitios con cadena; {sum(1 for r in rows if r['is_jog'])} son [JOG]")


if __name__ == "__main__":
    main()
