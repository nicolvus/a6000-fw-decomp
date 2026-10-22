#!/usr/bin/env python3
"""S139 — identifica las funciones del subsistema `McAvcEnc*` por sus cadenas.

Para cada función (delimitada por prólogos Thumb) recoge **todas** las cadenas
referenciadas por PIC dentro de su rango y saca de ahí:
  * el fichero fuente (`*.cpp` / `*.h`),
  * el nombre de la función (`__PRETTY_FUNCTION__`: "Int32 McAvcEncSeqCtrl::Exec..."),
  * las trazas `[ENCSEQCTRL]` que emite.

Uso: .venv/bin/python analysis/s139_encseqctrl/func_ident.py [LO] [HI]
"""
import json
import os
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


def cstr(addr):
    o = addr - BASE
    e = B.find(b"\0", o)
    return B[o:e].decode("latin1")


def main():
    lo = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x435d0000
    hi = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x435d9300
    # índice inverso: sitio -> destino
    inv = {}
    for dest, sites in G.items():
        for s in sites:
            inv.setdefault(s, []).append(int(dest, 16))
    # Para cada función: cadenas referenciadas
    idx = [i for i, p in enumerate(P) if lo <= p < hi]
    out = []
    for k, i in enumerate(idx):
        f0 = P[i]
        f1 = P[idx[k + 1]] if k + 1 < len(idx) else hi
        strs = {}
        for s, dests in inv.items():
            if f0 <= s < f1:
                for d in dests:
                    strs.setdefault(d, []).append(s)
        if not strs:
            continue
        src = sorted(d for d in strs if cstr(d).endswith((".cpp", ".h")))
        pf = sorted(d for d in strs if "::" in cstr(d) and cstr(d)[0].isupper())
        tr = sorted(d for d in strs if cstr(d).startswith("["))
        out.append({
            "fn": hex(f0),
            "ficheros": [(hex(d), cstr(d)) for d in src],
            "metodos": [(hex(d), cstr(d)) for d in pf],
            "trazas": [(hex(d), cstr(d)[:70]) for d in tr],
            "n_cadenas": len(strs),
        })
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
