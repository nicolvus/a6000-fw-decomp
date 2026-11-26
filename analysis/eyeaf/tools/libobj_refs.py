#!/usr/bin/env python3
"""Busca en .text de libObj.so los sitios que materializan direcciones concretas de .rodata
(movw/movt, `ldr rX,[pc,+d]` ... `add rX,pc`, adr). Pensado para un conjunto pequeno de
objetivos: memoria acotada. Salida JSON por stdout.

Uso: libobj_refs.py BIN 0xADDR[,0xADDR...]    |    libobj_refs.py BIN @fichero_de_direcciones
Solo estatico."""
import json, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM

PATH = sys.argv[1]
spec = sys.argv[2]
if spec.startswith('@'):
    targets = {int(x.strip(), 16) for x in open(spec[1:]) if x.strip() and not x.startswith('#')}
else:
    targets = {int(x, 16) for x in spec.split(',')}
TEXT_VA, TEXT_SIZE = 0x0e2b70, 0xae6a1c
data = open(PATH, 'rb').read()
code = data[TEXT_VA:TEXT_VA + TEXT_SIZE]


def read(va, n):
    off = va - 0x8000 if va >= 0xfd29d0 else va
    return data[off:off + n]


def u32(va):
    b = read(va, 4)
    return int.from_bytes(b, 'little') if len(b) == 4 else 0


cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
cs.detail = True
cs.skipdata = True
regs = {}
hits = {t: [] for t in targets}
for ins in cs.disasm(code, TEXT_VA):
    if ins.id == 0:
        continue
    m = ins.mnemonic
    ops = ins.operands
    val = None
    if m.startswith('movw') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
        regs[ins.reg_name(ops[0].reg)] = ops[1].imm & 0xffff
        continue
    if m.startswith('movt') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
        r = ins.reg_name(ops[0].reg)
        val = (((ops[1].imm & 0xffff) << 16) | (regs.get(r) or 0)) & 0xffffffff
        regs[r] = val
    elif m.startswith('ldr') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_MEM and ins.reg_name(ops[1].mem.base) == 'pc':
        lit = ((ins.address + 4) & ~3) + ops[1].mem.disp
        regs[ins.reg_name(ops[0].reg)] = u32(lit)
        continue
    elif m.startswith('add'):
        if len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc':
            base = regs.get(ins.reg_name(ops[0].reg))
            if base is not None:
                val = (((ins.address + 4) & ~3) + base) & 0xffffffff
                regs[ins.reg_name(ops[0].reg)] = val
        elif len(ops) >= 3 and ops[1].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc' and ops[2].type == ARM_OP_IMM:
            val = (((ins.address + 4) & ~3) + ops[2].imm) & 0xffffffff
            regs[ins.reg_name(ops[0].reg)] = val
        else:
            continue
    else:
        continue
    if val in hits:
        hits[val].append(ins.address)
json.dump({hex(k): v for k, v in hits.items()}, sys.stdout)
print()
