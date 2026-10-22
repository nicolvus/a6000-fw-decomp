#!/usr/bin/env python3
"""Desensamblador Thumb mínimo (uso interno de S132)."""
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
D = open("analysis/rea-independent/input/av-cam.bin", "rb").read()


def dis(lo, hi, skipdata=True):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    if skipdata:
        md.skipdata = True
    off = lo - BASE
    for i in md.disasm(D[off:off + (hi - lo)], lo):
        print(f"0x{i.address:x}: {i.mnemonic} {i.op_str}")


def prologues(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", D, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = struct.unpack_from("<H", D, o + 2)[0]
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


if __name__ == "__main__":
    dis(int(sys.argv[1], 0), int(sys.argv[2], 0))
