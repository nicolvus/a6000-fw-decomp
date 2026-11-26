#!/usr/bin/env python3
"""Desensamblador anotado mínimo (solo estático) para av-cam.bin cargado en 0x43541000.
Resuelve `ldr rX,[pc,#k]` (+ valor de la literal pool) y el idiomático `add rX,pc` -> dirección
absoluta y cadenas. Tolerante a huecos: salta 2 bytes cuando el flujo no decodifica.
Uso: avdis.py 0xDIR [TAM] [--raw]
"""
import struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM, ARM_REG_PC

BASE = 0x43541000
BIN = ('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter'
       '/analysis/rea-independent/input/av-cam.bin')
DATA = open(BIN, 'rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.detail = True


def off(a):
    return a - BASE


def rd32(a):
    o = off(a)
    if o < 0 or o + 4 > len(DATA):
        return None
    return struct.unpack_from('<I', DATA, o)[0]


def cstr(a, n=200):
    o = off(a)
    if o < 0 or o >= len(DATA):
        return None
    e = DATA.find(b'\0', o, o + n)
    if e < 0:
        return None
    try:
        s = DATA[o:e].decode('utf-8')
    except UnicodeDecodeError:
        return None
    return s if all(32 <= ord(c) < 127 for c in s) else None


def dis(start, size, extra=()):
    lits = {}
    out = []
    pos = 0
    endoff = off(start) + size
    while pos < size and endoff <= len(DATA):
        last = None
        for i in md.disasm(DATA[off(start) + pos:endoff], start + pos):
            last = i.address + i.size - start
            txt = f'{i.address:08x}  {i.mnemonic:8s} {i.op_str}'
            notes = []
            ops = i.operands
            if ops and i.mnemonic in ('ldr', 'ldrb', 'ldrh') and ops[0].type == ARM_OP_REG \
               and len(ops) == 2 and ops[1].type == ARM_OP_MEM and ops[1].mem.base == ARM_REG_PC:
                lit = ((i.address + 4) & ~3) + ops[1].mem.disp
                v = rd32(lit)
                r = i.op_str.split(',')[0].strip()
                lits[r] = (lit, v)
                notes.append(f'#{v:#010x}@{lit:08x}' if v is not None else '?')
                if v is not None:
                    s2 = cstr(v)
                    if s2 and len(s2) >= 4:
                        notes.append(f'"{s2[:70]}"')
            r0 = i.op_str.split(',')[0].strip()
            if i.mnemonic == 'add' and len(ops) == 2 and ops[0].type == ARM_OP_REG \
               and ops[1].type == ARM_OP_REG and ops[1].reg == ARM_REG_PC and r0 in lits and lits[r0][1] is not None:
                b = ((i.address + 4) & ~3) + lits[r0][1]
                notes.append(f'ADDR={b:#010x}')
                s2 = cstr(b)
                if s2 and len(s2) >= 4:
                    notes.append(f'"{s2[:90]}"')
                lits.pop(r0, None)
            for a in extra:
                if f'{a:08x}' in i.op_str:
                    notes.append(f'REF {a:#x}')
            if notes:
                txt += '    ; ' + ' | '.join(notes)
            out.append(txt)
        if last is None:
            out.append(f'{start + pos:08x}  .word    0x{rd32(start + pos) or 0:08x}   ; datos')
            pos += 4
        else:
            pos = last
    return '\n'.join(out)


if __name__ == '__main__':
    a = int(sys.argv[1], 16)
    n = int(sys.argv[2], 16) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 0x200
    print(dis(a, n))
