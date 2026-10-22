#!/usr/bin/env python3
"""S138 — localizadores de llamadas/ramificaciones hacia direcciones concretas.

Considera: `bl` (T1), `b` (T2/T4), `blx` (T2) y punteros absolutos de 32 bits
(con y sin bit Thumb). Salida: JSON + resumen por consola.
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()


def find_refs(targets):
    tset = set(targets)
    out = {t: {"bl": [], "b": [], "blx_imm": [], "abs_ptr": []} for t in targets}
    for a in range(BASE, BASE + len(B) - 4, 2):
        o = a - BASE
        h1, h2 = struct.unpack_from("<HH", B, o)
        if (h1 & 0xF800) == 0xE000:                # b T2 (16 bits): 11100 imm11
            s = (h1 & 0x7FF) << 1
            if s & 0x400:
                s -= 0x800
            d = (a + 4 + s) & 0xFFFFFFFF
            if d in tset:
                out[d]["b"].append(a)
            continue
        if (h1 & 0xF800) != 0xF000:
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        d = (a + 4 + s) & 0xFFFFFFFF
        if d not in tset:
            continue
        kind = None
        if (h2 & 0xD000) == 0xD000:
            kind = "bl"
        elif (h2 & 0xD000) == 0xC000:
            kind = "blx_imm"
        elif (h2 & 0xD000) == 0x8000:
            kind = "b"
        if kind:
            out[d][kind].append(a)
    for t in targets:
        for v in (t, t | 1):
            pat = struct.pack("<I", v)
            i = B.find(pat)
            while i >= 0:
                out[t]["abs_ptr"].append((BASE + i, "odd" if v & 1 else "even"))
                i = B.find(pat, i + 1)
    return out


def main():
    targets = [int(x, 16) for x in sys.argv[1:]]
    res = find_refs(targets)
    for t in targets:
        r = res[t]
        print(f"0x{t:x}: bl={len(r['bl'])} {[hex(x) for x in r['bl']]} "
              f"b={len(r['b'])} {[hex(x) for x in r['b']]} "
              f"blx_imm={len(r['blx_imm'])} "
              f"abs_ptr={[(hex(a),k) for a,k in r['abs_ptr']]}")
    json.dump({f"0x{t:x}": res[t] for t in targets},
              open(os.path.join(ROOT, "analysis/s138_camera_main_fc/fc_refs_all.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
