#!/usr/bin/env python3
"""S136 — desensamblado mínimo (Thumb) para verificar sitios PIC a mano.

Uso: .venv/bin/python analysis/s136_accy/disasm.py 0x43562a08 0x43562a60
"""
import struct
import sys

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"


def main():
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16) if len(sys.argv) > 2 else lo + 0x80
    data = open(BIN, "rb").read()
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    for ins in md.disasm(data[lo - BASE:hi - BASE], lo):
        print(f"{ins.address:#x}  {ins.bytes.hex():<12} {ins.mnemonic:<8} {ins.op_str}")


if __name__ == "__main__":
    main()
