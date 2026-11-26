#!/usr/bin/env python3
"""Índice de referencias PIC de av-cam.bin (solo estático).

Recorre la imagen en Thumb-2 con salto de huecos y resuelve el idiomático
`ldr rX,[pc,#k]` + `add rX,pc` -> dirección absoluta (base de datos, global, cadena).
Salida: refs_pic.json  { "AAAABBCC": [[sitio, modo], ...] }  con modo = 'pair' | 'adr'
Uso:  refs_pic.py                 (todas las referencias)
      refs_pic.py 0x43eb3af8      (solo un objetivo)
"""
import json
import struct
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_MEM, ARM_REG_PC

ROOT = ('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/eyeaf/avcam_eye_native/')
BIN = ('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter'
       '/analysis/rea-independent/input/av-cam.bin')
BASE = 0x43541000
DATA = open(BIN, 'rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.detail = True

def rd32(a):
    o = a - BASE
    if o < 0 or o + 4 > len(DATA):
        return None
    return struct.unpack_from('<I', DATA, o)[0]

N = len(DATA)
WIN = 0x40000
pending = {}          # reg -> (site_ldr, literal_value, addr_of_literal)
refs = {}
pos = 0
insns = 0
while pos < N:
    last = None
    for i in md.disasm(DATA[pos:pos + WIN], BASE + pos):
        insns += 1
        last = i.address + i.size
        ops = i.operands
        if i.mnemonic in ('ldr', 'ldrb', 'ldrh') and len(ops) == 2 and ops[0].type == ARM_OP_REG \
           and ops[1].type == ARM_OP_MEM and ops[1].mem.base == ARM_REG_PC:
            rn = i.reg_name(ops[0].reg)
            lit_addr = ((i.address + 4) & ~3) + ops[1].mem.disp
            pending[rn] = (i.address, rd32(lit_addr))
            continue
        if i.mnemonic in ('add', 'addw') and len(ops) >= 2 and ops[0].type == ARM_OP_REG:
            rn = i.reg_name(ops[0].reg)
            srcs = [i.reg_name(o.reg) for o in ops[1:] if o.type == ARM_OP_REG]
            if ARM_REG_PC in [o.reg for o in ops[1:] if o.type == ARM_OP_REG] and rn in pending:
                v = pending.pop(rn)[1]
                if v is not None:
                    tgt = ((i.address + 4) & ~3) + v
                    refs.setdefault(f'{tgt:08x}', []).append([i.address, 'pair'])
                continue
            # propagación simple: mov/add de registro a registro
            if len(ops) == 2 and ops[1].type == ARM_OP_REG and srcs and srcs[0] in pending:
                pending[rn] = pending[srcs[0]]
                continue
        if i.mnemonic in ('add', 'addw'):
            # adr: add rX, pc, #imm
            if len(ops) == 3 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_REG \
               and ops[1].reg == ARM_REG_PC and ops[2].type == 2:  # ARM_OP_IMM
                tgt = ((i.address + 4) & ~3) + ops[2].imm
                refs.setdefault(f'{tgt:08x}', []).append([i.address, 'adr'])
            continue
        pending.pop(i.reg_name(ops[0].reg), None) if ops and ops[0].type == ARM_OP_REG else None
    if last is None:
        pos += 2
    else:
        end = last - BASE
        pos = end if end >= pos + WIN - 4 else end + 2

print(json.dumps({'insns': insns, 'targets': len(refs)}), file=sys.stderr)
json.dump(refs, open(ROOT + 'refs_pic.json', 'w'))
