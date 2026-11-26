#!/usr/bin/env python3
"""Version generica (cualquier ELF ARM32 de la camara) de la busqueda de sitios que
materializan direcciones de .rodata: movw/movt, `ldr rX,[pc,+d]` + `add rX,pc`, adr.

Uso: elf_refs.py BIN @fichero_de_direcciones | 0xA,0xB,...
Salida: JSON { "0x<destino>": [sitios] } por stdout. Solo estatico."""
import json, re, struct, subprocess, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM

PATH = sys.argv[1]
spec = sys.argv[2]
targets = ({int(x.strip(), 16) for x in open(spec[1:]) if x.strip() and not x.startswith('#')}
           if spec.startswith('@') else {int(x, 16) for x in spec.split(',')})
out = subprocess.run(['readelf', '-SW', PATH], capture_output=True, text=True).stdout
SEC = {}
for line in out.splitlines():
    m = re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
    if m:
        n, t, a, o, z = m.groups()
        SEC[n] = (int(a, 16), None if t == 'NOBITS' else int(o, 16), int(z, 16))
D = open(PATH, 'rb').read()


def va2off(va):
    for n, (a, o, z) in SEC.items():
        if o is not None and a <= va < a + z:
            return o + (va - a)
    return None


def u32(va):
    o = va2off(va)
    if o is None:
        return 0
    return int.from_bytes(D[o:o + 4], 'little')


tva, toff, tsz = SEC['.text']
options = [] if '--arm' not in sys.argv else [CS_MODE_ARM]
cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN if not options else CS_MODE_ARM + CS_MODE_LITTLE_ENDIAN)
cs.detail = True
cs.skipdata = True
regs = {}
hits = {t: [] for t in targets}
for ins in cs.disasm(D[toff:toff + tsz], tva):
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
        regs[ins.reg_name(ops[0].reg)] = u32(((ins.address + 4) & ~3) + ops[1].mem.disp)
        continue
    elif m.startswith('add'):
        if len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc':
            b = regs.get(ins.reg_name(ops[0].reg))
            if b is not None:
                val = (((ins.address + 4) & ~3) + b) & 0xffffffff
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
