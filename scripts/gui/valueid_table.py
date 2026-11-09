#!/usr/bin/env python3
"""G26 — tabla de nombres VALUEID de `libObj.so` (array de punteros contiguo, relocs R_ARM_RELATIVE): índice → nombre. Uso: valueid_table.py LIB"""
import struct, subprocess, sys
from pathlib import Path


def tabla(lib: Path, ancla=b"VALUEID_PP_COLOR_STD\0"):
    d = lib.read_bytes()
    out = subprocess.run(["readelf", "-lW", str(lib)], capture_output=True, text=True, check=True).stdout
    segs = [(int(x[1], 16), int(x[2], 16), int(x[4], 16)) for x in (l.split() for l in out.splitlines()) if x and x[0] == "LOAD"]

    def foff(va):
        for o, v, s in segs:
            if v <= va < v + s:
                return o + va - v

    rel = set()
    for l in subprocess.run(["readelf", "-rW", str(lib)], capture_output=True, text=True, check=True).stdout.splitlines():
        f = l.split()
        if len(f) >= 3 and f[2] == "R_ARM_RELATIVE":
            rel.add(int(f[0], 16))
    tgt = d.find(ancla)
    base = next(a for a in sorted(rel) if struct.unpack_from("<I", d, foff(a))[0] == tgt)
    ini = base
    while ini - 4 in rel:
        ini -= 4
    fin = base
    while fin in rel:
        fin += 4
    res = []
    for a in range(ini, fin, 4):
        p = struct.unpack_from("<I", d, foff(a))[0]
        e = d.index(b"\0", p)
        res.append(d[p:e].decode("latin1"))
    return res, (base - ini) // 4


if __name__ == "__main__":
    t, i0 = tabla(Path(sys.argv[1]))
    print(len(t), "ancla en índice", i0, t[0], t[1], t[-1])
    for i, n in enumerate(t):
        if "_PP_" in n and "EXC_CONF" not in n:
            print(i, n)
