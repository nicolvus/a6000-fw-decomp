#!/usr/bin/env python3
"""S119 — diferencial A7S fw3.20: donde esta el codigo que emite las trazas `[APL]`.

Verifica la base vaddr = 0x43541000 + offset tambien en el blob de la A7S
(resolviendo el esquema PIC) y devuelve las funciones emisoras.
"""
import json
import os
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
MAX_GAP = 4096

B = open(A7S, "rb").read()
N = len(B)


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = o
    while e < N and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def starts():
    out = set()
    prev = False
    for i in range(N):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 8:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((a + 4) & ~3) + imm12
        if reg is None:
            continue
        o2 = lit - BASE
        if 0 <= o2 <= N - 4:
            out.append((a, reg, struct.unpack_from("<I", B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def prologues(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > N - 4:
            break
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
    return out


def main():
    st = starts()
    ldrs = ldr_sites(BASE, BASE + N)
    adds = add_sites(BASE, BASE + N)
    by_reg = defaultdict(list)
    for a, reg, w in ldrs:
        by_reg[reg].append((a, w))
    for v in by_reg.values():
        v.sort()
    # trazas [APL] de la A7S
    traces = []
    i = 0
    while True:
        i = B.find(b"[APL]", i)
        if i < 0:
            break
        e = i
        while e < N and 32 <= B[e] < 127:
            e += 1
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        traces.append((BASE + s, BASE + i, B[s:e].decode("latin1")))
        i += 1
    seen = set()
    uniq = []
    for t in traces:
        if t[0] in seen:
            continue
        seen.add(t[0])
        uniq.append(t)
    want = {t[0]: t for t in uniq}
    refs = defaultdict(list)
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        best = None
        for la, w in reversed(v):
            if la > a or a - la > MAX_GAP:
                continue
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            if best is None:
                best = (tgt, la)
            if tgt in want:
                refs[tgt].append((a, la))
            break
    cands = sorted(prologues(BASE, BASE + N))

    def func_of(site):
        import bisect
        i = bisect.bisect_right(cands, site) - 1
        while i >= 0:
            c = cands[i]
            if site - c > 0x4000:
                break
            limit = cands[i + 1] if i + 1 < len(cands) else c + 0x4000
            if site < limit:
                return c
            i -= 1
        return None

    out = []
    by_func = defaultdict(list)
    for full, tag, text in uniq:
        sites = refs.get(full, [])
        fs = sorted({func_of(s) for s, _ in sites})
        out.append({"vaddr_full": f"0x{full:x}", "vaddr_tag": f"0x{tag:x}",
                    "text": text,
                    "sites": [f"0x{s:x}" for s, _ in sites],
                    "funcs": [f"0x{f:x}" if f else None for f in fs]})
        for f in fs:
            by_func[f"0x{f:x}" if f else None].append(f"0x{tag:x}")
    res = {"a7s_base": hex(BASE), "n_traces": len(uniq),
           "funcs": {k: len(v) for k, v in sorted(by_func.items(), key=lambda kv: -len(kv[1]))},
           "traces": out}
    json.dump(res, open(os.path.join(HERE, "apl_a7s_map.json"), "w"), indent=1,
              ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "traces"}, indent=1))


if __name__ == "__main__":
    main()
