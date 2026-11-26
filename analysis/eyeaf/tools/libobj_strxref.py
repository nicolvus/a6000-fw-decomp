#!/usr/bin/env python3
"""Barrido lineal de .text de libObj.so (Thumb-2): registra los sitios que materializan la
dirección de una cadena de .rodata (movw/movt, `ldr rX,[pc,+d]` + `add rX,pc`, adr).
Salida JSON { "0x<addr_cadena>": [direcciones de instrucción que la construyen] }.
Solo estático; no se ejecuta nada del binario."""
import json, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM

PATH, OUT = sys.argv[1], sys.argv[2]
TEXT_VA, TEXT_SIZE = 0x0e2b70, 0xae6a1c
RO_LO, RO_HI = 0xbc9598, 0xe91fb2
data = open(PATH, 'rb').read()

def read(va, n):
    off = va - 0x8000 if va >= 0xfd29d0 else va
    return data[off:off + n]

def u32(va):
    b = read(va, 4)
    return int.from_bytes(b, 'little') if len(b) == 4 else 0

# conjunto de direcciones que inician una cadena imprimible (>=6 bytes)
starts = set()
ro = data[RO_LO:RO_HI]
i = 0
while i < len(ro):
    if 32 <= ro[i] < 127 and (i == 0 or ro[i - 1] == 0):
        j = i
        while j < len(ro) and 32 <= ro[j] < 127:
            j += 1
        if j - i >= 6 and j < len(ro) and ro[j] == 0:
            starts.add(RO_LO + i)
        i = j
    else:
        i += 1

cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
cs.detail = True
cs.skipdata = True
code = data[TEXT_VA:TEXT_VA + TEXT_SIZE]
regs = {}
hits = {}
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
        val = ((ops[1].imm & 0xffff) << 16) | (regs.get(r) or 0)
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
    if val in starts:
        hits.setdefault(hex(val), []).append(ins.address)
json.dump(hits, open(OUT, 'w'))
print('strings', len(starts), 'targets', len(hits), 'sites', sum(len(v) for v in hits.values()))
