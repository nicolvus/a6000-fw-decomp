#!/usr/bin/env python3
"""Utilidad S139: para un conjunto de tokens, lista cadenas → sitios PIC (regla estricta)
→ función (prólogo) y rango de código.

Uso: .venv/bin/python analysis/s139_encseqctrl/sites_of_tokens.py TOKEN [TOKEN...]
"""
import bisect
import json
import os
import re
import struct
import sys

BASE = 0x43541000
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")
CODE_LO, CODE_HI = 0x43541000, 0x43A00000

B = open(BIN, "rb").read()
G = json.load(open(GLOBAL))


def prologues():
    out = []
    a = CODE_LO
    while a < CODE_HI:
        h = struct.unpack_from("<H", B, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", B, a - BASE + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


P = prologues()


def fstart(site):
    i = bisect.bisect_right(P, site) - 1
    return P[i] if i >= 0 else None


def strings_with(token):
    out = []
    for m in re.finditer(re.escape(token.encode()), B):
        s = m.start()
        while s > 0 and B[s - 1] != 0 and 32 <= B[s - 1] < 127:
            s -= 1
        e = B.find(b"\0", m.start())
        out.append((BASE + s, B[s:e].decode("latin1")))
    return out


def main():
    for token in sys.argv[1:]:
        rows = []
        for addr, text in sorted(set(strings_with(token))):
            sites = G.get(hex(addr), [])
            rows.append((addr, text, sites))
        fs = {}
        for addr, text, sites in rows:
            for s in sites:
                fs.setdefault(fstart(s), []).append((s, addr))
        print(f"=== {token}: {len(rows)} cadenas, "
              f"{sum(len(r[2]) for r in rows)} sitios, {len(fs)} funciones")
        if len(fs) <= 40:
            for f in sorted(fs):
                lo = min(x[0] for x in fs[f])
                hi = max(x[0] for x in fs[f])
                print(f"   fn 0x{f:x}  sitios={len(fs[f]):3d}  rango 0x{lo:x}-0x{hi:x}")


if __name__ == "__main__":
    main()
