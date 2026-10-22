#!/usr/bin/env python3
"""S123 — desensamblado de un rango (verificación a mano de los sitios PIC).

Uso:  disasm.py LO HI [--pool]
"""
import struct
import sys

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    lo = int(sys.argv[1], 0)
    hi = int(sys.argv[2], 0)
    fh = open(BIN, "rb")
    fh.seek(lo - BASE)
    data = fh.read(hi - lo)
    fh.close()
    for ins in md.disasm(data, lo):
        raw = ins.bytes.hex()
        extra = ""
        if ins.mnemonic.startswith("ldr") and "pc" in ins.op_str:
            # literal pool: ((addr+4)&~3) + imm
            a = ins.address
            h = struct.unpack_from("<H", data, a - lo)[0]
            if (h & 0xF800) == 0x4800:
                lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
            else:
                h2 = struct.unpack_from("<H", data, a + 2 - lo)[0]
                lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
            off = lit - BASE
            fh2 = open(BIN, "rb")
            fh2.seek(off)
            w = struct.unpack_from("<I", fh2.read(4))[0]
            fh2.close()
            extra = f"   ; pool@{lit:#x} W={w:#x}"
        print(f"{ins.address:#010x}  {raw:10s}  {ins.mnemonic:8s} {ins.op_str}{extra}")


if __name__ == "__main__":
    main()
