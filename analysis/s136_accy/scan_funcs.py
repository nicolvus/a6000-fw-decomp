#!/usr/bin/env python3
"""S136 — qué其它 cadenas referencia el código del módulo `[ACCY]`.

Para cada función de la región ACCY (0x43562a08..0x43567000) se listan todos los
destinos PIC (mapa global) cuyo `add rX,pc` cae dentro de la función, no solo las
cadenas `[ACCY]`.

Uso: .venv/bin/python analysis/s136_accy/scan_funcs.py
"""
import json
import os
import struct
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
HERE = os.path.dirname(os.path.abspath(__file__))
ACCY_LO, ACCY_HI = 0x43562a08, 0x43567000


def prologues(data, lo, hi):
    out = []
    a = lo
    n = len(data)
    while a < hi:
        o = a - BASE
        if o < 0 or o + 4 > n:
            a += 2
            continue
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and (struct.unpack_from("<H", data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def main():
    data = open(BIN, "rb").read()
    g = json.load(open(GLOBAL))
    # destinos -> sitios
    dest2sites = {int(k, 16): v for k, v in g.items()}
    starts = prologues(data, ACCY_LO, ACCY_HI)
    # todos los sitios en la región ACCY
    sites_region = []
    for dest, ss in dest2sites.items():
        for s in ss:
            if ACCY_LO <= s < ACCY_HI:
                sites_region.append((s, dest))
    sites_region.sort()
    print(f"sitios PIC totales en la región ACCY: {len(sites_region)}")
    print(f"funciones (prólogo) en la región: {len(starts)}")
    # agrupa por función
    def encl(addr):
        cand = [x for x in starts if x <= addr]
        return cand[-1] if cand else None
    byfunc = defaultdict(list)
    for s, dest in sites_region:
        byfunc[encl(s)].append((s, dest))
    out = {}
    for f, lst in byfunc.items():
        out[f"0x{f:x}"] = [{"site": f"0x{s:x}", "dest": f"0x{d:x}"} for s, d in lst]
    with open(os.path.join(HERE, "accy_funcs.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    # volcar los destinos no-[ACCY]
    print("\n--- destinos fuera de [ACCY] ---")
    seen = set()
    for s, dest in sites_region:
        if dest in seen:
            continue
        seen.add(dest)
        o = dest - BASE
        e = data.find(b"\x00", o)
        txt = data[o:e].decode("latin1") if 0 <= o < len(data) else "?"
        if not txt.startswith("[ACCY]"):
            print(f"0x{dest:x}  {txt[:100]!r}")


if __name__ == "__main__":
    main()
