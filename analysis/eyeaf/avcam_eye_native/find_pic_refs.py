#!/usr/bin/env python3
"""Busca sitios PIC (`ldr rX,[pc,#k]` + `add rX,pc`) que materialicen una dirección dada.

Heurística: para cada palabra de 32 bits V en la imagen, si A = T - V es una dirección
alineada a 4 dentro de +-0x4000 de la posición de la literal, se verifica decodificando
la instrucción en A (o en A-2/A+2) y comprobando que sea `ldr rX,[pc,#k]` con
k = D - align(A+4). Solo análisis estático.

Uso: find_pic_refs.py 0x43eb3bf4 [0x43eb3af8 ...]
"""
import struct
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_MEM, ARM_REG_PC

BASE = 0x43541000
BIN = ('/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter'
       '/analysis/rea-independent/input/av-cam.bin')
DATA = open(BIN, 'rb').read()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.detail = True


def insn_at(a):
    o = a - BASE
    if o < 0 or o + 4 > len(DATA):
        return None
    for ins in md.disasm(DATA[o:o + 4], a):
        return ins
    return None


def find(T):
    out = []
    for D in range(BASE, BASE + len(DATA) - 4, 4):
        V = struct.unpack_from('<I', DATA, D - BASE)[0]
        A = (T - V) & 0xffffffff
        if not (0x43541000 <= A < 0x44027000):
            continue
        if abs(A - D) > 0x4000:
            continue
        for cand in range(A - 18, A + 1, 2):
            ins = insn_at(cand)
            if ins is None or ins.mnemonic != 'ldr':
                continue
            ops = ins.operands
            if len(ops) != 2 or ops[0].type != ARM_OP_REG or ops[1].type != ARM_OP_MEM \
               or ops[1].mem.base != ARM_REG_PC:
                continue
            if ((ins.address + 4) & ~3) + ops[1].mem.disp != D:
                continue
            out.append((ins.address, D, ins.op_str, ins.reg_name(ops[0].reg)))
            break
    return out


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        T = int(arg, 16)
        hits = find(T)
        print(f'== {T:#010x}: {len(hits)} sitios PIC')
        for a, d, op, reg in hits:
            print(f'   {a:#010x}  ldr {op}   (literal {d:#010x})')
