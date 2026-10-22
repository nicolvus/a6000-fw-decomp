#!/usr/bin/env python3
"""S148 — localizadores de llamadas `bl`/`blx` (16 y 32 bits) a un objetivo.

Usa capstone en modo Thumb sobre toda la imagen (skipdata) y recoge los
destinos de `bl`/`blx`.

Uso:  .venv/bin/python analysis/s148_depth/callers.py 0x43541b02 0x435626d4
"""
import os
import sys
from collections import defaultdict

import capstone

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
md.detail = False
md.skipdata = True


def build():
    out = defaultdict(list)
    for ins in md.disasm(B, BASE):
        if ins.mnemonic in ("bl", "blx", "b", "b.w"):
            tgt = ins.op_str
            if tgt.startswith("#"):
                try:
                    v = int(tgt[1:], 0)
                except ValueError:
                    continue
                out[v & ~1].append(ins.address)
    return out


def main():
    m = build()
    for x in sys.argv[1:]:
        t = int(x, 0) & ~1
        sites = m.get(t, [])
        print(f"target 0x{t:08x}: {len(sites)} call sites")
        for s in sites[:60]:
            print(f"    0x{s:08x}")


if __name__ == "__main__":
    main()
