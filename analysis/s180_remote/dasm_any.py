#!/usr/bin/env python3
"""S180 - desensamblado de un rango en CUALQUIER firmware (A6000/A7S/A6300)."""
import sys
from capstone import *

BASE = 0x43541000
BINS = {
    "A6000": "analysis/rea-independent/input/av-cam.bin",
    "A7S": "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
    "A6300": "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin",
}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = True


def cstr(B, a):
    o = a - BASE
    if o < 0 or o >= len(B):
        return "<fuera>"
    e = o
    while e < len(B) and 32 <= B[e] < 127:
        e += 1
    return B[o:e].decode("latin1")


def main():
    which = sys.argv[1]
    lo = int(sys.argv[2], 0)
    hi = int(sys.argv[3], 0)
    B = open(BINS[which], "rb").read()
    # capstone 5 decodifica mal desde una direccion IMPAR: se alinea a par y se
    # anota el bit de Thumb en el primer argumento.
    start = lo & ~1
    for i in md.disasm(B[start - BASE:hi - BASE], start):
        extra = ""
        if i.mnemonic in ("bl", "blx", "b", "b.w"):
            try:
                extra = f"  ; -> 0x{i.operands[0].imm:08x}"
            except Exception:
                pass
        print(f"0x{i.address:08x}  {i.mnemonic:<8} {i.op_str}{extra}")


if __name__ == "__main__":
    main()
