#!/usr/bin/env python3
"""Busca llamadas directas (BL/BLX inmediato) a una lista de destinos dentro de un rango de
.text de libObj.so.  Uso: libobj_callers.py 0xLO 0xHI 0xT1,0xT2,...
Solo estatico."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_IMM

PATH = 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'
lo = int(sys.argv[1], 16)
hi = int(sys.argv[2], 16)
targets = {int(x, 16) for x in sys.argv[3].split(',')}
data = open(PATH, 'rb').read()
data = data[:0] + open(PATH, 'rb').read()
code = data[lo:hi]
cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
cs.detail = True
cs.skipdata = True
for ins in cs.disasm(code, lo):
    if ins.id == 0:
        continue
    if ins.mnemonic in ('bl', 'blx') and len(ins.operands) == 1 and ins.operands[0].type == ARM_OP_IMM:
        t = ins.operands[0].imm & ~1
        if t in targets:
            print(hex(ins.address), '->', hex(t))
