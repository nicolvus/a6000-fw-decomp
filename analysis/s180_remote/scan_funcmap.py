#!/usr/bin/env python3
"""S180 - mapa funcion -> traza para el sub-bloque [REMOTE] (y el bloque ACCY entero)."""
import json, struct, os
from collections import defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
GLOBAL = "analysis/s106_imaging_cap/pic_refs_strict_global.json"
ACCY_LO, ACCY_HI = 0x43562000, 0x43567400

B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from


def prologues(data, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o + 4 > N:
            a += 2
            continue
        h = U16(data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and (U16(data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def cstr(a):
    o = a - BASE
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


g = json.load(open(GLOBAL))
sites = []
for dest, ss in g.items():
    for s in ss:
        if ACCY_LO <= s < ACCY_HI:
            sites.append((s, int(dest, 16)))
sites.sort()
starts = prologues(B, ACCY_LO, ACCY_HI)
print(f"sitios PIC en la region: {len(sites)}; prologos: {len(starts)}")


def encl(addr):
    cand = [x for x in starts if x <= addr]
    return cand[-1] if cand else None


byfunc = defaultdict(list)
for s, d in sites:
    byfunc[encl(s)].append((s, d))

remote = json.load(open("analysis/s180_remote/pic_sites.json"))["strings"]
rem_vaddrs = {r["vaddr"] for r in remote}

out = {"funcs": {}, "remote_funcs": {}}
print()
print("--- funciones que emiten trazas [REMOTE] ---")
for f in sorted(byfunc):
    items = byfunc[f]
    isrem = any(d in rem_vaddrs for _, d in items)
    if not isrem:
        continue
    out["remote_funcs"][f"0x{f:x}"] = [
        {"site": f"0x{s:x}", "dest": f"0x{d:x}", "text": cstr(d)} for s, d in items]
    print(f"0x{f:x}  ({len(items)} sitios REMOTE / {len(items)} totales en la funcion)")
    for s, d in items:
        mark = "REMOTE" if d in rem_vaddrs else "     "
        print(f"    {mark} site 0x{s:x} -> 0x{d:x}  {cstr(d)[:90]!r}")

print()
print("--- todas las funciones de la region y sus destinos ---")
for f in sorted(byfunc):
    items = byfunc[f]
    tags = sorted({("[REMOTE]" if d in rem_vaddrs else cstr(d).split("]:")[0] + "]" if cstr(d).startswith("[") else "OTRA")
                   for _, d in items})
    out["funcs"][f"0x{f:x}"] = [{"site": f"0x{s:x}", "dest": f"0x{d:x}", "text": cstr(d)}
                                for s, d in items]
    print(f"0x{f:x}  n={len(items):2d}  {tags}")

json.dump(out, open("analysis/s180_remote/func_map.json", "w"), indent=1)
