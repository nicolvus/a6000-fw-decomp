#!/usr/bin/env python3
"""S118 — censo de llamadas desde las funciones de `[SFRA]`.

Para cada función que referencia una traza `[SFRA]` se listan sus destinos de
llamada (`bl`), agrupados por módulo de código, para documentar con qué
subsistemas se relaciona `[SFRA]`.
"""
import json
import os
import re
import sys
from collections import Counter

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_sfra import BASE, BIN, CODE_HI, CODE_LO, function_ranges  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    data = open(BIN, "rb").read()
    smap = {}
    for s, lst in json.load(open(os.path.join(HERE, "site_best.json"))).items():
        smap[int(s, 16)] = int(lst[0], 16)
    ranges = function_ranges(data, CODE_LO, CODE_HI)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False

    # funciones SFRA (las 47 del mapa de funciones)
    fm = json.load(open(os.path.join(HERE, "func_map.json")))
    sfra_funcs = [(int(f["func"], 16), None) for f in fm["functions"]]
    ends = {}
    for fs, fe in ranges:
        ends[fs] = fe
    sfra_funcs = [(fs, ends[fs]) for fs, _ in sfra_funcs if fs in ends]

    calls = Counter()
    calls_from = {}
    for fs, fe in sorted(sfra_funcs):
        for ins in md.disasm(data[fs - BASE:fe - BASE], fs):
            if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#"):
                t = int(ins.op_str.lstrip("#"), 16) & ~1
                calls[t] += 1
                calls_from.setdefault(t, set()).add(fs)
    print("funciones [SFRA]:", len(sfra_funcs))
    print("destinos de llamada distintos:", len(calls))
    # agrupación por rangos de 64 KB
    buckets = Counter()
    for t, n in calls.items():
        buckets[t >> 16] += n
    for k in sorted(buckets):
        print("  0x%08x-0x%08x : %d llamadas" % (k << 16, (k << 16) | 0xffff, buckets[k]))
    json.dump({"n_funcs": len(sfra_funcs),
               "calls": {f"0x{t:x}": n for t, n in calls.items()},
               "calls_from": {f"0x{t:x}": sorted(f"0x{f:x}" for f in v)
                              for t, v in calls_from.items()}},
              open(os.path.join(HERE, "call_census.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
