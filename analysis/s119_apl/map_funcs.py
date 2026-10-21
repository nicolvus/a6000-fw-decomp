#!/usr/bin/env python3
"""S119 — mapa funcion -> traza `[APL]` con las dos reglas de emparejamiento PIC.

  canonico : todos los `ldr` del registro dentro de 4 KB (regla del repo)
  estricto : solo el `ldr` del registro mas cercano por debajo (4 KB)

Salida: analysis/s119_apl/apl_map.json
"""
import bisect
import json
import os
import struct
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
MAX_GAP = 4096
CODE_LO, CODE_HI = BASE, 0x43C90000

B = open(BIN, "rb").read()


def cstr(a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return None
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1") if e > o else None


def starts():
    out = set()
    prev = False
    for i in range(len(B)):
        cur = 32 <= B[i] < 127
        if cur and not prev:
            out.add(BASE + i)
        prev = cur
    return out


def ldr_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 8:
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
        if 0 <= o2 <= len(B) - 4:
            out.append((a, reg, struct.unpack_from("<I", B, o2)[0]))
    return out


def add_sites(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 4:
            continue
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
    return out


def prologues(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 4:
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


def pops(lo, hi):
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 4:
            break
        h = struct.unpack_from("<H", B, o)[0]
        if (h & 0xFF00) == 0xBD00 and (h & 0x8000):
            out.append(a)
            continue
        if h == 0xE8BD:
            out.append(a)
    return out


def main():
    st = starts()
    ldrs = ldr_sites(CODE_LO, CODE_HI)
    adds = add_sites(CODE_LO, CODE_HI)
    by_reg = defaultdict(list)
    for a, reg, w in ldrs:
        by_reg[reg].append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    canon = defaultdict(list)
    strict = defaultdict(list)
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_left(ks, a) - 1
        best = None
        while i >= 0:
            la, w = v[i]
            if a - la > MAX_GAP:
                break
            tgt = (w + (a + 4)) & 0xFFFFFFFF
            # regla estricta: el `ldr` mas cercano POR DEBAJO es el bueno
            if best is None:
                best = (tgt, la)
            if tgt in st:
                canon[tgt].append((a, la))
            i -= 1
        if best and best[0] in st:
            strict[best[0]].append((a, best[1]))

    # trazas [APL]
    traces = []
    tag = b"[APL]"
    i = 0
    while True:
        i = B.find(tag, i)
        if i < 0:
            break
        e = i
        while e < len(B) and 32 <= B[e] < 127:
            e += 1
        s = i
        while s > 0 and 32 <= B[s - 1] < 127:
            s -= 1
        traces.append({
            "vaddr_full": f"0x{BASE + s:x}",
            "vaddr_tag": f"0x{BASE + i:x}",
            "text": B[s:e].decode("latin1"),
        })
        i += 1
    # deduplicar por cadena completa
    seen = set()
    uniq = []
    for t in traces:
        if t["vaddr_full"] in seen:
            continue
        seen.add(t["vaddr_full"])
        uniq.append(t)

    cands = sorted(prologues(CODE_LO, CODE_HI))
    pk = pops(CODE_LO, CODE_HI)
    pk = sorted(pk)

    def func_of(site):
        i = bisect.bisect_right(cands, site) - 1
        while i >= 0:
            c = cands[i]
            if site - c > 0x4000:
                break
            limit = cands[i + 1] if i + 1 < len(cands) else c + 0x4000
            j = bisect.bisect_right(pk, site)
            if j < len(pk) and pk[j] <= limit:
                return c
            i -= 1
        return None

    out = []
    for t in uniq:
        a = int(t["vaddr_full"], 16)
        cs = canon.get(a, [])
        ss = strict.get(a, [])
        out.append({
            **t,
            "canon": [{"site": f"0x{s:x}", "ldr": f"0x{l:x}",
                       "func": (f"0x{func_of(s):x}" if func_of(s) else None)}
                      for s, l in sorted(cs)],
            "strict": [{"site": f"0x{s:x}", "ldr": f"0x{l:x}",
                        "func": (f"0x{func_of(s):x}" if func_of(s) else None)}
                       for s, l in sorted(ss)],
        })
    json.dump({"module": "[APL]", "n": len(out), "traces": out},
              open(os.path.join(HERE, "apl_map.json"), "w"), indent=1,
              ensure_ascii=False)

    # resumen por funcion (estricto y canonico)
    def by_func(key):
        d = defaultdict(list)
        for t in out:
            for x in t[key]:
                d[x["func"]].append(t["vaddr_tag"])
        return {k: sorted(set(v)) for k, v in sorted(d.items(), key=lambda kv: -len(kv[1]))}

    print("estricto:", json.dumps({k: len(v) for k, v in by_func("strict").items()}, indent=1))
    print("canonico:", json.dumps({k: len(v) for k, v in by_func("canon").items()}, indent=1))
    print("n_traces", len(out))
    for t in out:
        print(t["vaddr_tag"], t["text"][:56],
              "| canon:", [(x["site"], x["func"]) for x in t["canon"]],
              "| strict:", [(x["site"], x["func"]) for x in t["strict"]])


if __name__ == "__main__":
    main()
