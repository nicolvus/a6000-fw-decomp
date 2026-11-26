#!/usr/bin/env python3
"""Barrido lineal estático de av-cam.bin (Thumb-2) con salto de huecos no decodificables."""
import json, struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM
ROOT='/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/eyeaf/avcam_eye_native/'
BASE = 0x43541000
DATA = open('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin','rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN); md.detail = True
N = len(DATA); WIN = 0x40000
INTEREST = {0xde,0xdf,0xe0,0xe2,0xe4,0xe6,0xdb,0xdc,0xdd,0xd7,0x49c,0x49e,0x4a0,0x4a2,0x56}
hits=[]; pos=0; insns=0; gaps=0
while pos < N:
    last = None
    end = pos
    for i in md.disasm(DATA[pos:pos+WIN], BASE+pos):
        insns += 1
        last = i.address + i.size
        for k in i.operands:
            if k.type == ARM_OP_MEM and k.mem.disp in INTEREST and (k.mem.base or k.mem.index):
                hits.append({'addr': i.address, 'mn': i.mnemonic, 'op': i.op_str, 'disp': k.mem.disp,
                             'write': i.mnemonic.startswith('str')})
    if last is None:
        pos += 2; gaps += 1; continue
    end = last - BASE
    if end >= pos + WIN - 4:
        pos = end            # ventana agotada, seguimos
    else:
        pos = end + 2; gaps += 1   # instrucción inválida
print(json.dumps({'insns': insns, 'gaps': gaps, 'hits': len(hits)}), file=sys.stderr)
json.dump(hits, open(ROOT+'field_access.json','w'), indent=0)
