#!/usr/bin/env python3
"""Diferencial del modulo `[TRK]` entre A6000 fw3.21 y A7S fw3.20.

Extrae las cadenas `[TRK` de los dos blobs, compara el multiconjunto de textos
y, con el mismo emparejamiento PIC de `scan_refs.py`, cuenta cadenas
referenciadas / sitios / funciones en cada uno.

Salida: analysis/s111_trk/a7s_diff.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan_refs as S

HERE = os.path.dirname(os.path.abspath(__file__))
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
HI = 0x43C00000


def runs(path):
    d = open(path, "rb").read()
    out = []
    i = 0
    while True:
        i = d.find(b"[TRK", i)
        if i < 0:
            break
        j = i
        while j < len(d) and 32 <= d[j] < 127:
            j += 1
        out.append((S.BASE + i, d[i:j].decode("latin1")))
        i = j if j > i else i + 1
    return out


def profile(path, strs):
    data = open(path, "rb").read()
    targets = {a: {"vaddr": hex(a), "text": t} for a, t in strs}
    refs = S.scan_refs(data, S.BASE, HI, targets)
    funcs = S.prologue_ends(data, S.BASE, HI)
    starts = [f[0] for f in funcs]
    owners = set()
    strict = relaxed = 0
    for t, hits in refs.items():
        for site, _l, _w, _c in hits:
            f, kind = S.owner(site, funcs, starts)
            if f:
                owners.add(f)
            strict += kind == "strict"
            relaxed += kind == "relaxed"
    return {"n_runs": len(strs), "n_strings": len(targets),
            "n_referenced": len(refs),
            "n_sites": sum(len(v) for v in refs.values()),
            "n_sites_strict": strict, "n_sites_relaxed": relaxed,
            "n_functions": len(owners),
            "lo": hex(min(t for t, _ in strs)), "hi": hex(max(t for t, _ in strs))}


def main():
    a = runs(A6000)
    b = runs(A7S)
    ca, cb = {}, {}
    for _v, t in a:
        ca[t] = ca.get(t, 0) + 1
    for _v, t in b:
        cb[t] = cb.get(t, 0) + 1
    only_a = sorted(set(ca) - set(cb))
    only_b = sorted(set(cb) - set(ca))
    out = {"a6000": profile(A6000, a), "a7s": profile(A7S, b),
           "only_a6000": only_a, "only_a7s": only_b,
           "identical_texts": not only_a and not only_b,
           "identical_multiset": ca == cb}
    json.dump(out, open(os.path.join(HERE, "a7s_diff.json"), "w"),
              indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("only_a6000", "only_a7s")}, indent=1))


if __name__ == "__main__":
    main()
