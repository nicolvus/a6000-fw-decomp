#!/usr/bin/env python3
"""S138 — utilidades de desensamblado y de límites de función (bytes, sin REA/Ghidra).

Convención: vaddr = 0x43541000 + file_offset.

Uso:
  .venv/bin/python analysis/s138_camera_main_fc/disasm.py 0x437b7200 0x437b7400
  .venv/bin/python analysis/s138_camera_main_fc/disasm.py 0x437b7200 0x437b7400 --funcs
"""
import os
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x43541000
BIN = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = True


def disasm(lo, hi):
    return list(MD.disasm(B[lo - BASE:hi - BASE], lo))


def bl_targets(lo, hi):
    """Conjunto de destinos de `bl`/`blx` directos en el rango."""
    out = set()
    for a in range(lo, hi - 4, 2):
        o = a - BASE
        h1 = B[o] | (B[o + 1] << 8)
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = B[o + 2] | (B[o + 3] << 8)
        if (h2 & 0xD000) != 0xD000:
            continue
        s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
        if s & 0x400000:
            s -= 0x800000
        out.add((a + 4 + s) & 0xFFFFFFFF)
    return out


def is_prologue(ins):
    """push.w {... lr} o push {... lr}"""
    if ins.mnemonic != "push":
        return False
    return "lr" in ins.op_str


def func_starts(lo, hi):
    """Heurística de inicio de función: destinos de `bl` + prólogos con lr."""
    starts = set(bl_targets(lo, hi))
    for ins in disasm(lo, hi):
        if is_prologue(ins) and ins.address % 2 == 0:
            starts.add(ins.address)
    return sorted(starts)


def enclosing(addr, starts):
    best = None
    for s in starts:
        if s <= addr:
            best = s
        else:
            break
    return best


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16) if len(sys.argv) > 2 else lo + 0x100
    if "--funcs" in sys.argv:
        for s in func_starts(lo, hi):
            print(f"func 0x{s:x}")
        return
    for ins in disasm(lo, hi):
        print(f"0x{ins.address:08x}  {ins.mnemonic:8s} {ins.op_str}")


if __name__ == "__main__":
    main()
