#!/usr/bin/env python3
"""S127 — inicios de función por los destinos de `bl`/`blx` (32 bits Thumb).

Barrido por bytes del encoding:
  primera mitad  : 11110 S imm10   (0xF000-0xF7FF, con bit 11 = 1)
  segunda mitad  : 11 J1 1 J2 imm11 (0xD000-0xEFFF para `bl`, 0xC000-0xCFFF para `blx`)
No depende de desensamblar linealmente, así que no se desincroniza con los datos
intercalados. Devuelve el conjunto ordenado de destinos en el rango de código.
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
LO, HI = 0x43541000, 0x43A00000


def bl_targets(data):
    out = set()
    n = len(data)
    for off in range(0, n - 3, 2):
        h1, h2 = struct.unpack_from("<HH", data, off)
        if (h1 & 0xF800) != 0xF000:
            continue
        op = h2 & 0xD000
        if op not in (0xD000, 0xC000):
            continue
        s = (h1 >> 10) & 1
        imm10 = h1 & 0x03FF
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        imm11 = h2 & 0x07FF
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            imm -= 1 << 25
        src = BASE + off
        tgt = src + 4 + imm
        if LO <= tgt < HI:
            out.add(tgt)
    return sorted(out)


def resolve(sites, targets):
    """Para cada sitio, el destino de `bl` más cercano <= sitio (el inicio de función)."""
    import bisect
    out = []
    for s in sites:
        i = bisect.bisect_right(targets, s) - 1
        out.append(targets[i] if i >= 0 else None)
    return out


if __name__ == "__main__":
    data = open(BIN, "rb").read()
    t = bl_targets(data)
    print(len(t), hex(t[0]), hex(t[-1]))
    for a in sys.argv[1:]:
        addr = int(a, 16)
        import bisect
        i = bisect.bisect_right(t, addr) - 1
        print(f"site 0x{addr:x} -> func 0x{t[i]:x}")
