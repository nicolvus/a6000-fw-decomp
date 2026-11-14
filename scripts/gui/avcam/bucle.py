#!/usr/bin/env python3
"""bucle.py PC [PC…]: desensambla el bucle de sondeo de av-cam alrededor de PC y resuelve los literales (direcciones de registros)."""
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from liro_vm import AVCAM, BASE

d = AVCAM.read_bytes()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
for a in (int(x, 16) for x in sys.argv[1:]):
    ini = a - 0x28
    print(f"== {a:#x}")
    for i in md.disasm(d[ini - BASE:ini - BASE + 0x40], ini):
        extra = ""
        if i.mnemonic.startswith("ldr") and "[pc, #" in i.op_str:
            lit = ((i.address + 4) & ~3) + int(i.op_str.split("#")[1].rstrip("]"), 16)
            extra = f"   ; = {struct.unpack_from('<I', d, lit - BASE)[0]:#x}"
        print(f"{'>' if i.address == a else ' '} {i.address:#x} {i.mnemonic} {i.op_str}{extra}")
