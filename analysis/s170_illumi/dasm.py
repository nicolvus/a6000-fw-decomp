#!/usr/bin/env python3
"""S170 — desensamblador mínimo (Thumb) con anotación de pares PIC.

Uso:  dasm.py 0x435acdd0 0x435ace60
"""
import bisect
import struct
import sys

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

BASE = 0x43541000
B = open("analysis/rea-independent/input/av-cam.bin", "rb").read()
N = len(B)
U32 = struct.Struct("<I").unpack_from
U16 = struct.Struct("<H").unpack_from


def cstr(a):
    o = a - BASE
    if o < 0 or o >= N:
        return None
    e = B.find(b"\x00", o)
    if e < 0:
        return None
    try:
        return B[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None


def ldr_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def disasm(lo, hi):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    code = B[lo - BASE:hi - BASE]
    ldrs = ldr_sites(lo, hi)
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    for ins in md.disasm(code, lo):
        s = f"{ins.address:#010x}  {ins.mnemonic:<8} {ins.op_str}"
        if ins.mnemonic == "add" and "pc" in ins.op_str:
            h = U16(B, ins.address - BASE)[0]
            if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
                reg = (((h >> 7) & 1) << 3) | (h & 7)
                v = by_reg.get(reg)
                if v:
                    ks = keys[reg]
                    i = bisect.bisect_right(ks, ins.address) - 1
                    if i >= 0:
                        la, w, lit = v[i]
                        if ins.address - la <= 4096:
                            dest = (w + ins.address + 4) & 0xFFFFFFFF
                            s += (f"   ; PIC ldr@{la:#x} pool@{lit:#x}={w:#x}"
                                  f" -> {dest:#x} {cstr(dest)!r}")
        print(s)


if __name__ == "__main__":
    disasm(int(sys.argv[1], 0), int(sys.argv[2], 0))
