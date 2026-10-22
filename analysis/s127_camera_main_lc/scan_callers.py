#!/usr/bin/env python3
"""S127 — busca los `bl`/`blx` que apuntan a una dirección dada (encoding Thumb-2).

  scan_callers.py 0x437c1e48 [0x43754be0 ...]

Barrido por bytes (no desensambla linealmente), así que no se desincroniza con
los datos intercalados. vaddr = 0x43541000 + file_offset.
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def callers(data, wanted):
    out = {w: [] for w in wanted}
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
        if tgt in out:
            out[tgt].append(src)
    return out


if __name__ == "__main__":
    data = open(BIN, "rb").read()
    wanted = {int(a, 16) for a in sys.argv[1:]}
    res = callers(data, wanted)
    for t in sorted(res):
        sites = res[t]
        print(f"0x{t:x}\t{len(sites)}\t" + ",".join(f"0x{s:x}" for s in sites))
