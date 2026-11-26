#!/usr/bin/env python3
"""Barrido de escrituras/lecturas de los campos de ojo del registro de cara (Camera::FC/LC)."""
import json, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM
ROOT='/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/eyeaf/avcam_eye_native/'
BASE = 0x43541000
DATA = open('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin','rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN); md.detail = True
N = len(DATA); WIN = 0x40000
INTEREST = {0x56,0x58,0x59,0x5a,0x5b,0x5c,0x5d,0x5e,0x5f,0x60}
hits=[]; pos=0; insns=0
while pos < N:
    last = None
    for i in md.disasm(DATA[pos:pos+WIN], BASE+pos):
        insns += 1
        last = i.address + i.size
        for k in i.operands:
            if k.type == ARM_OP_MEM and k.mem.disp in INTEREST and (k.mem.base or k.mem.index):
                hits.append({'addr': i.address, 'mn': i.mnemonic, 'op': i.op_str, 'disp': k.mem.disp,
                             'write': i.mnemonic.startswith('str')})
    if last is None:
        pos += 2
    else:
        end = last - BASE
        pos = end if end >= pos + WIN - 4 else end + 2
print(json.dumps({'insns': insns, 'hits': len(hits)}), file=sys.stderr)
json.dump(hits, open(ROOT+'eye_fields.json','w'), indent=0)
