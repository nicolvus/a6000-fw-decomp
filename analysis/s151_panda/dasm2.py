#!/usr/bin/env python3
"""S151 - desensamblador auxiliar multi-blob (capstone) con anotacion PIC + cadenas.

Uso:  .venv/bin/python analysis/s151_panda/dasm2.py <a7s|a6300|a6000> LO HI
"""
import bisect
import os
import struct
import sys

import capstone

BASE = 0x43541000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BLOBS = {
    "a6000": "analysis/rea-independent/input/av-cam.bin",
    "a7s": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "a6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
MAX_LDR_GAP = 4096


def main():
    which = sys.argv[1]
    lo = int(sys.argv[2], 0)
    hi = int(sys.argv[3], 0)
    B = open(os.path.join(REPO, BLOBS[which]), "rb").read()
    U16 = struct.Struct("<H").unpack_from
    U32 = struct.Struct("<I").unpack_from
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True

    def pool_at(addr):
        o = addr - BASE
        if 0 <= o <= len(B) - 4:
            return U32(B, o)[0]
        return None

    def cstr(off, maxlen=120):
        e = off
        while e < len(B) and e < off + maxlen and (32 <= B[e] < 127 or B[e] in (9, 10)):
            e += 1
        return B[off:e].decode("latin-1")

    ldrs = []
    for a in range(max(BASE, lo - MAX_LDR_GAP), hi, 2):
        o = a - BASE
        if o < 0 or o > len(B) - 8:
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
        if reg is not None:
            w = pool_at(lit)
            if w is not None:
                ldrs.append((a, reg, w))
    by = {}
    for a, reg, w in ldrs:
        by.setdefault(reg, []).append((a, w))
    for v in by.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by.items()}

    for ins in md.disasm(B[lo - BASE:hi - BASE], lo):
        note = ""
        full = f"{ins.mnemonic} {ins.op_str}"
        if ins.mnemonic in ("ldr", "ldr.w") and "[pc" in ins.op_str:
            try:
                imm = int(ins.op_str.split("#")[-1].rstrip("]"), 0)
            except ValueError:
                imm = None
            if imm is not None:
                lit = ((ins.address + 4) & ~3) + imm
                w = pool_at(lit)
                if w is not None:
                    note += f"  ; pool@0x{lit:08x}=0x{w:08x}"
        if ins.mnemonic == "add" and ins.op_str.endswith(", pc"):
            rn = ins.op_str.split(",")[0].strip()
            aliases = {"ip": 12, "sp": 13, "lr": 14, "pc": 15, "sb": 9, "sl": 10, "fp": 11}
            r = aliases[rn] if rn in aliases else int(rn.lstrip("r"))
            v = by.get(r)
            if v:
                i = bisect.bisect_right(keys[r], ins.address) - 1
                if i >= 0 and ins.address - v[i][0] <= MAX_LDR_GAP:
                    tgt = (v[i][1] + ins.address + 4) & 0xFFFFFFFF
                    if BASE <= tgt < BASE + len(B):
                        note += f"  ; -> 0x{tgt:08x} {cstr(tgt - BASE)!r}"
        raw = B[ins.address - BASE:ins.address - BASE + ins.size].hex()
        print(f"0x{ins.address:08x}  {raw:<10} {ins.mnemonic} {ins.op_str}{note}")


if __name__ == "__main__":
    main()
