#!/usr/bin/env python3
"""S138 — de qué fichero fuente (y qué cadenas) depende una función.

Dado el inicio de una función, calcula sus sitios PIC (mapa global estricto) y
lista las cadenas a las que apunta, con su vaddr. Sirve para atribuir un
`.cpp` a una función cuando la traza lo cita (`file=%s line=%d`).
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
GLOBAL = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")
B = open(BIN, "rb").read()


def prologues(lo, hi):
    out = []
    a = lo
    while a < hi:
        h = struct.unpack_from("<H", B, a - BASE)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (struct.unpack_from("<H", B, a - BASE + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def cstr(off):
    e = B.find(b"\x00", off)
    return B[off:e].decode("latin1")


def main():
    entry = int(sys.argv[1], 16)
    size = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x400
    g = json.load(open(GLOBAL))
    inv = {}
    for dest, sites in g.items():
        for s in sites:
            inv.setdefault(int(s), []).append(int(dest, 16))
    rows = []
    for site in sorted(inv):
        if not (entry <= site < entry + size):
            continue
        for dest in inv[site]:
            off = dest - BASE
            if 0 <= off < len(B):
                rows.append((site, dest, cstr(off)))
    print(f"funcion 0x{entry:x}: {len(rows)} sitios PIC")
    for site, dest, txt in rows:
        print(f"  sitio 0x{site:x} -> 0x{dest:x}  {txt[:120]!r}")
    ps = [p for p in prologues(entry - 0x400, entry + size) if p <= entry]
    print("prólogo previo:", [hex(p) for p in ps[-3:]])


if __name__ == "__main__":
    main()
