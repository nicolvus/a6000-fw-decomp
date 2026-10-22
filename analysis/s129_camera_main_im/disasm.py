#!/usr/bin/env python3
"""S129 — utilidades de desensamblado y de xrefs de código (bytes, sin REA/Ghidra).

Convención: vaddr = 0x43541000 + file_offset.

Uso:
  .venv/bin/python analysis/s129_camera_main_im/disasm.py 0x437b8774 0x437b8a00
"""
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def md():
    m = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    m.detail = True
    return m


def disasm(data, lo, hi):
    m = md()
    return list(m.disasm(data[lo - BASE:hi - BASE], lo))


def bl_starts(data, target, lo=0x43541000, hi=0x44017000, thumb=True):
    """Busca `bl` directos a `target` (y su variante par/impar)."""
    out = []
    t = target & ~1
    for a in range(lo, hi - 4, 2):
        o = a - BASE
        h1 = data[o] | (data[o + 1] << 8)
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = data[o + 2] | (data[o + 3] << 8)
        if (h2 & 0xD000) != 0xD000:
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        dest = (a + 4 + s) & 0xFFFFFFFF
        if dest == t or dest == (target | 1):
            out.append(a)
    return out


def abs_refs(data, target, lo=0x43541000, hi=0x44017000):
    """Apariciones del valor de 32 bits `target` (posible puntero de función)."""
    pat = target.to_bytes(4, "little")
    out = []
    i = data.find(pat)
    while i >= 0:
        out.append(BASE + i)
        i = data.find(pat, i + 1)
    return out


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16) if len(sys.argv) > 2 else lo + 0x100
    data = open(BIN, "rb").read()
    for ins in disasm(data, lo, hi):
        print(f"0x{ins.address:x}  {ins.mnemonic:8s} {ins.op_str}")


if __name__ == "__main__":
    main()
