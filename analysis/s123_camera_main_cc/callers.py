#!/usr/bin/env python3
"""S123 — **llamadores** de las funciones que emiten trazas `[CAMERA_MAIN_CC]`.

Recorre todo el código del binario buscando instrucciones `bl`/`blx` cuyo destino
sea una de las 29 funciones del módulo (o una de las funciones de etapa) y
asigna el llamador a su función (prólogo + epílogo, capstone).

Uso:  callers.py [SALIDA]
"""
import json
import os
import struct
import bisect
from collections import defaultdict

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
HERE = os.path.dirname(os.path.abspath(__file__))
MAX_FUNC = 0x8000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True


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
    dest = os.path.join(HERE, "callers.json")
    fmap = json.load(open(os.path.join(HERE, "func_map.json")))
    targets = {int(f["func"], 16): f["func"] for f in fmap["functions"]}
    data = open(BIN, "rb").read()
    n = len(data)
    code = data
    prols = prologues(code)
    end_cache = {}

    def f_end(rel):
        if rel not in end_cache:
            end_cache[rel] = func_end(code, rel, BASE)
        return end_cache[rel]

    def owner(site):
        rel = site - BASE
        i = bisect.bisect_right(prols, rel) - 1
        while i >= 0:
            p = prols[i]
            if rel - p > MAX_FUNC:
                break
            e = f_end(p)
            if e is not None and BASE + p <= site <= e:
                return (BASE + p, e)
            i -= 1
        return None

    # referencia inversa: cadena -> módulo
    refs = json.load(open("/tmp/opencode/pic_strict_global.json"))
    mod_of = {}
    for tgt in refs:
        t = int(tgt, 16)
        off = t - BASE
        if off < 0 or off >= n:
            continue
        e = off
        while e < n and e < off + 120 and 32 <= data[e] < 127:
            e += 1
        txt = data[off:e].decode("latin1")
        if txt.startswith("[") and "]" in txt:
            mod_of[t] = txt[1:txt.index("]")]
    site_mod = defaultdict(set)
    for tgt, sites in refs.items():
        m = mod_of.get(int(tgt, 16))
        if m:
            for s in sites:
                site_mod[s].add(m)

    callers = defaultdict(list)
    for ins in md.disasm(code, BASE):
        if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#"):
            t = int(ins.op_str[1:], 16)
            if t in targets:
                o = owner(ins.address)
                mods = sorted(site_mod.get(o[0], [])) if o else []
                callers[targets[t]].append(
                    {"site": f"0x{ins.address:x}",
                     "caller": f"0x{o[0]:x}" if o else None,
                     "caller_end": f"0x{o[1]:x}" if o else None,
                     "caller_modules": mods})
    out = {k: v for k, v in sorted(callers.items())}
    json.dump({"module": "CAMERA_MAIN_CC", "callers": out},
              open(dest, "w"), indent=1, ensure_ascii=False)
    total = sum(len(v) for v in out.values())
    print(f"funciones del módulo con llamadores: {len(out)}  llamadas: {total}")
    for k, v in out.items():
        mods = sorted({m for c in v for m in c["caller_modules"]})
        print(f"  {k}  <- {len(v)} llamadas  módulos llamadores: {mods}")


if __name__ == "__main__":
    main()
