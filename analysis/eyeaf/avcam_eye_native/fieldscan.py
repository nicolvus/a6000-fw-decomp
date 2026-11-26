#!/usr/bin/env python3
"""Barrido genérico: accesos [base+disp] para los desplazamientos pedidos.
Uso: fieldscan.py 0x1d3 0x65 ...   -> escribe fieldscan_<n>.json"""
import json, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_MEM
ROOT='/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/eyeaf/avcam_eye_native/'
BASE = 0x43541000
DATA = open('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin','rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN); md.detail = True
INTEREST = {int(a,16) for a in sys.argv[1:]}
N=len(DATA); WIN=0x40000; pos=0; hits=[]
while pos < N:
    last=None
    for i in md.disasm(DATA[pos:pos+WIN], BASE+pos):
        last = i.address + i.size
        for k in i.operands:
            if k.type == ARM_OP_MEM and k.mem.disp in INTEREST and (k.mem.base or k.mem.index):
                hits.append({'addr': i.address, 'mn': i.mnemonic, 'op': i.op_str,
                             'disp': k.mem.disp, 'write': i.mnemonic.startswith('str')})
    if last is None:
        pos += 2
    else:
        end = last - BASE
        pos = end if end >= pos + WIN - 4 else end + 2
print(json.dumps({'hits': len(hits)}), file=sys.stderr)
tag='_'.join(f'{x:x}' for x in sorted(INTEREST))
json.dump(hits, open(ROOT+f'fieldscan_{tag}.json','w'))
