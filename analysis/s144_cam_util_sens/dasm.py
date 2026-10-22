#!/usr/bin/env python3
"""S144 — desensamblador auxiliar (capstone) con anotacion PIC + cadenas.

Uso:  .venv/bin/python analysis/s144_cam_util_sens/dasm.py 0x439012d0 0x43901380

Marca los pares PIC `ldr rX,[pc,#imm]` + `add rX,pc` (regla estricta) con su
destino resuelto, y los destinos de llamada `bl`/`blx`.
"""
import bisect
import os
import re
import struct
import sys

import capstone

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BIN = os.path.join(REPO, "analysis/rea-independent/input/av-cam.bin")
B = open(BIN, "rb").read()
MAX_LDR_GAP = 4096

md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
md.detail = True


def cstr(off, maxlen=200):
    e = off
    while e < len(B) and e < off + maxlen and 32 <= B[e] < 127:
        e += 1
    return B[off:e].decode("latin-1")


def pool_at(addr):
    o = addr - BASE
    if 0 <= o <= len(B) - 4:
        return struct.unpack_from("<I", B, o)[0]
    return None


def build_ldrs(lo, hi):
    ldrs = []
    for a in range(lo, hi, 2):
        o = a - BASE
        h = struct.unpack_from("<H", B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            w = pool_at(lit)
            if w is not None:
                ldrs.append((a, reg, w))
    return ldrs


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    ldrs = build_ldrs(max(BASE, lo - MAX_LDR_GAP), hi)
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    for ins in md.disasm(B[lo - BASE:hi - BASE], lo):
        note = ""
        m = re.match(r"^(ldr|ldr\.w)\s+(r\d+),\s*\[pc,\s*#?(0x[0-9a-f]+|\d+)\]", ins.op_str)
        if m:
            imm = int(m.group(3), 0)
            lit = ((ins.address + 4) & ~3) + imm
            w = pool_at(lit)
            if w is not None:
                note += f"  ; pool@0x{lit:08x}=0x{w:08x} reg={m.group(2)}"
        m2 = re.match(r"^add\s+(r\d+),\s*pc", ins.op_str)
        if m2:
            reg = m2.group(1)
            idx = {"r0": 0, "r1": 1, "r2": 2, "r3": 3, "r4": 4, "r5": 5, "r6": 6, "r7": 7}
            r = idx[reg]
            v = by_reg.get(r)
            if v:
                i = bisect.bisect_right(keys[r], ins.address) - 1
                if i >= 0:
                    la, w = v[i]
                    if ins.address - la <= MAX_LDR_GAP:
                        tgt = (w + ins.address + 4) & 0xFFFFFFFF
                        s = cstr(tgt - BASE) if BASE <= tgt < BASE + len(B) else ""
                        note += f"  ; -> 0x{tgt:08x} {s!r}"
        if ins.mnemonic in ("bl", "blx", "b.w", "b"):
            note += "  ; CALL/BRANCH"
        raw = B[ins.address - BASE:ins.address - BASE + ins.size].hex()
        print(f"0x{ins.address:08x}  {raw:<10} {ins.mnemonic} {ins.op_str}{note}")


if __name__ == "__main__":
    main()
