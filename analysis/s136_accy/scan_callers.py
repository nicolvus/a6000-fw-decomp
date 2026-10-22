#!/usr/bin/env python3
"""S136 — llamadores externos del módulo `[ACCY]`: función que contiene el `bl` y
cadenas que referencia esa función (para saber desde qué módulo se llama).

Uso: .venv/bin/python analysis/s136_accy/scan_callers.py
"""
import json
import os
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
ACCY_LO, ACCY_HI = 0x43562000, 0x43567000


def prologues(data):
    out = []
    a = BASE
    n = len(data)
    while a < BASE + n:
        o = a - BASE
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (struct.unpack_from("<H", data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def main():
    data = open(BIN, "rb").read()
    g = json.load(open(GLOBAL))
    d2s = {int(k, 16): v for k, v in g.items()}
    site2dest = {}
    for dest, ss in d2s.items():
        for s in ss:
            site2dest[s] = dest
    calls = json.load(open(os.path.join(HERE, "accy_calls.json")))
    into = calls["into"]
    starts = prologues(data)

    def encl(addr):
        lo, hi = 0, len(starts) - 1
        best = None
        while lo <= hi:
            mid = (lo + hi) // 2
            if starts[mid] <= addr:
                best = starts[mid]
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    rows = []
    for tgt, sites in into.items():
        for s in sites:
            if ACCY_LO <= s < ACCY_HI:
                continue
            f = encl(s)
            strs = []
            if f is not None:
                # cadenas referenciadas por la función que contiene el call
                for ss, dest in site2dest.items():
                    if f <= ss < f + 0x2000 and dest not in (0,):
                        o = dest - BASE
                        if 0 <= o < len(data):
                            e = data.find(b"\x00", o)
                            txt = data[o:e].decode("latin1")
                            if txt.startswith("[ACCY]"):
                                continue
                            strs.append((ss, dest, txt[:70]))
            rows.append((tgt, s, f, sorted(strs)[:6]))
    rows.sort(key=lambda r: (r[0], r[1]))
    for tgt, s, f, strs in rows:
        print(f"bl 0x{s:x} -> 0x{tgt}   (en func 0x{f:x})" if f else f"bl 0x{s:x} -> 0x{tgt}")
        for ss, d, t in strs:
            print(f"        0x{ss:x} 0x{d:x} {t!r}")


if __name__ == "__main__":
    main()
