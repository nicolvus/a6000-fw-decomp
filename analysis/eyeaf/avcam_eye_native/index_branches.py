#!/usr/bin/env python3
"""Índice de ramas (call graph grueso) de av-cam.bin: bl/b/b.w/blx con destino inmediato."""
import json, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_IMM
ROOT='/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/eyeaf/avcam_eye_native/'
BASE = 0x43541000
DATA = open('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin','rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN); md.detail = True
N = len(DATA); WIN = 0x40000
br = []; pos = 0; insns = 0; gaps = 0
while pos < N:
    last = None
    for i in md.disasm(DATA[pos:pos+WIN], BASE+pos):
        insns += 1
        last = i.address + i.size
        if i.mnemonic in ('bl', 'blx', 'b', 'b.w', 'bx') or i.mnemonic.startswith('b'):
            if i.operands and i.operands[-1].type == ARM_OP_IMM:
                br.append([i.address, i.mnemonic, i.operands[-1].imm])
    if last is None:
        pos += 2; gaps += 1; continue
    end = last - BASE
    pos = end if end >= pos + WIN - 4 else end + 2
    if last is not None and pos == end + 2: gaps += 1
json.dump({'insns': insns, 'gaps': gaps, 'branches': br}, open(ROOT+'branches.json','w'))
print(json.dumps({'insns': insns, 'gaps': gaps, 'branches': len(br)}), file=sys.stderr)
