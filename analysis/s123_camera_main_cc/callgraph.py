#!/usr/bin/env python3
"""S123 — grafo de llamadas desde las funciones de `[CAMERA_MAIN_CC]`.

Para cada función que emite una traza `[CAMERA_MAIN_CC]`:
  * se desensambla y se listan los destinos `bl`/`blx` (directos);
  * cada destino se asigna a su función (prólogo + epílogo, capstone);
  * se calcula el **módulo** ([PREFIX]) al que pertenece cada función llamada:
    el prefijo de las cadenas que esa función referencia (mapa PIC estricto).

Salida: `callgraph.json`.

Uso:  callgraph.py [REFS_GLOBAL_JSON] [SALIDA]
"""
import json
import os
import struct
import bisect
import sys
from collections import defaultdict

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_FUNC = 0x8000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def prologues(code):
    out = []
    a = 0
    n = len(code)
    while a + 2 <= n:
        h = struct.unpack_from("<H", code, a)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and a + 4 <= n:
            h2 = struct.unpack_from("<H", code, a + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def func_end(code, start_rel, base_vaddr, limit=MAX_FUNC):
    for ins in md.disasm(code[start_rel:start_rel + limit], base_vaddr + start_rel):
        if ins.mnemonic.startswith("pop") and "pc" in ins.op_str:
            return ins.address
        if ins.mnemonic == "bx" and ins.op_str == "lr":
            return ins.address
    return None


def main():
    refs_path = (sys.argv[1] if len(sys.argv) > 1
                 else "/tmp/opencode/pic_strict_global.json")
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "callgraph.json")
    refs = json.load(open(refs_path))
    fmap = json.load(open(os.path.join(HERE, "func_map.json")))
    data = open(BIN, "rb").read()

    # --- módulo de cada cadena referenciada (por prefijo) --------------------
    mod_of = {}
    for tgt in refs:
        t = int(tgt, 16)
        off = t - BASE
        if off < 0 or off >= len(data):
            continue
        e = off
        while e < len(data) and e < off + 120 and 32 <= data[e] < 127:
            e += 1
        txt = data[off:e].decode("latin1")
        if txt.startswith("[") and "]" in txt:
            mod_of[t] = txt[1:txt.index("]")]

    inv_site = defaultdict(list)
    for tgt, sites in refs.items():
        for s in sites:
            inv_site[s].append(int(tgt, 16))

    cc_funcs = [(int(fn["func"], 16), int(fn["func_end"], 16), fn)
                for fn in fmap["functions"]]

    lo_c = min(a for a, _, _ in cc_funcs) - 0x2000
    hi_c = max(b for _, b, _ in cc_funcs) + 0x2000
    code = data[lo_c - BASE:hi_c - BASE]
    prols = prologues(code)
    end_cache = {}

    def f_end(rel):
        if rel not in end_cache:
            end_cache[rel] = func_end(code, rel, lo_c)
        return end_cache[rel]

    def owner(site):
        rel = site - lo_c
        i = bisect.bisect_right(prols, rel) - 1
        while i >= 0:
            p = prols[i]
            if rel - p > MAX_FUNC:
                break
            e = f_end(p)
            if e is not None and lo_c + p <= site <= e:
                return (lo_c + p, e)
            i -= 1
        return None

    # --- módulo de cada función (a partir de sus sitios de referencia) -------
    func_mods = defaultdict(set)
    for site, tgts in inv_site.items():
        o = owner(site)
        if not o:
            continue
        for t in tgts:
            m = mod_of.get(t)
            if m:
                func_mods[o[0]].add(m)

    # --- llamadas de cada función CC -----------------------------------------
    rows = []
    for a, b, fn in cc_funcs:
        callees = []
        seen = set()
        for ins in md.disasm(code[a - lo_c:b - lo_c + 4], a):
            if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#"):
                t = int(ins.op_str[1:], 16)
                if t in seen or t < BASE or t >= BASE + len(data):
                    continue
                seen.add(t)
                o = owner(t)
                mods = sorted(func_mods.get(o[0], [])) if o else []
                callees.append({"target": f"0x{t:x}",
                                "func": f"0x{o[0]:x}" if o else None,
                                "func_end": f"0x{o[1]:x}" if o else None,
                                "modules": mods})
        own = sorted(func_mods.get(a, []))
        rows.append({"func": fn["func"], "func_end": fn["func_end"],
                     "own_modules": own,
                     "traces": [s["text"] for s in fn["strings"]],
                     "callees": callees})

    json.dump({"module": "CAMERA_MAIN_CC", "functions": rows},
              open(dest, "w"), indent=1, ensure_ascii=False)
    print(f"funciones: {len(rows)} -> {dest}")
    for r in rows:
        mods = sorted({m for c in r["callees"] for m in c["modules"]})
        print(f"  {r['func']}  callees={len(r['callees']):2d}  modulos={mods}")


if __name__ == "__main__":
    main()
