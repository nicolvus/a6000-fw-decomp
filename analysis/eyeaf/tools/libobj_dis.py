#!/usr/bin/env python3
"""Desensamblado anotado de un rango de libObj.so (Thumb-2) con nombres .dynsym, PLT,
cadenas de .rodata (movw/movt, ldr[pc]+add) e inmediatos de 16/32 bits.

Uso: libobj_dis.py 0xINICIO 0xFIN [--struct r4]
Solo estatico."""
import struct, subprocess, sys, re
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM

PATH = 'firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so'
DATA = open(PATH, 'rb').read()


def read(va, n):
    off = va - 0x8000 if va >= 0xfd29d0 else va
    return DATA[off:off + n]


def u32(va):
    b = read(va, 4)
    return int.from_bytes(b, 'little') if len(b) == 4 else 0


def cstr(va, mx=110):
    if not (0xbc9598 <= va < 0xe91fb2):
        return None
    s = read(va, mx).split(b'\0')[0]
    try:
        t = s.decode('utf-8')
    except UnicodeDecodeError:
        return None
    return t if t and all(32 <= ord(c) < 127 for c in t) else None


def syms():
    out = subprocess.run(['readelf', '-sW', PATH], capture_output=True, text=True).stdout
    S = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[3] in ('FUNC', 'OBJECT', 'IFUNC') and f[1] != '00000000':
            try:
                a = int(f[1], 16) & ~1
            except ValueError:
                continue
            try:
                sz = int(f[2])
            except ValueError:
                sz = 0
            S.setdefault(a, (f[7], sz))
    return S


def plt():
    out = subprocess.run(['readelf', '-rW', PATH], capture_output=True, text=True).stdout
    got = []
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 5 and f[2] == 'R_ARM_JUMP_SLOT':
            got.append(((int(f[0], 16)), f[4]))
    got.sort()
    m = {}
    base = None
    for line in subprocess.run(['readelf', '-SW', PATH], capture_output=True, text=True).stdout.splitlines():
        mm = re.match(r'\s*\[\s*\d+\]\s+\.plt\s+\S+\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
        if mm:
            base = int(mm.group(1), 16)
    if base:
        for i, (_, nm) in enumerate(got):
            m[base + 12 + 12 * i] = nm
    return m


SYM = syms()
PLT = plt()


def annot(addr):
    s = cstr(addr)
    nm = SYM.get(addr & ~1)
    if addr in PLT:
        return 'plt:' + PLT[addr]
    if s:
        return '"' + s + '"'
    if nm:
        return nm[0]
    if addr in SYM:
        return SYM[addr][0]
    return None


def dump(start, end, struct_reg=None):
    cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
    cs.detail = True
    regs = {}
    out = []
    for ins in cs.disasm(read(start, end - start), start):
        if ins.id == 0:
            out.append('%08x  %-16s .byte' % (ins.address, ins.bytes.hex()))
            continue
        m = ins.mnemonic
        ops = ins.operands
        note = []
        val = None
        if m.startswith('movw') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
            regs[ins.reg_name(ops[0].reg)] = ops[1].imm & 0xffff
        elif m.startswith('movt') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
            r = ins.reg_name(ops[0].reg)
            val = (((ops[1].imm & 0xffff) << 16) | (regs.get(r) or 0)) & 0xffffffff
            regs[r] = val
        elif m.startswith('ldr') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_MEM and ins.reg_name(ops[1].mem.base) == 'pc':
            lit = ((ins.address + 4) & ~3) + ops[1].mem.disp
            regs[ins.reg_name(ops[0].reg)] = u32(lit)
        elif m.startswith('add') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc':
            r = ins.reg_name(ops[0].reg)
            base = regs.get(r)
            if base is not None:
                val = (((ins.address + 4) & ~3) + base) & 0xffffffff
                regs[r] = val
        elif m.startswith('add') and len(ops) >= 3 and ins.reg_name(ops[1].reg) == 'pc' and ops[2].type == ARM_OP_IMM:
            val = (((ins.address + 4) & ~3) + ops[2].imm) & 0xffffffff
            regs[ins.reg_name(ops[0].reg)] = val
        if val is not None:
            a = annot(val)
            if a:
                note.append(a[:100])
        if m.startswith('bl') and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
            t = ops[0].imm
            a = annot(t)
            note.append('-> ' + (a[:80] if a else '(sub)'))
            regs = {}
        elif m.startswith('b') and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
            note.append('-> loc_%x' % ops[0].imm)
            regs = {}
        elif m in ('blx',) and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
            a = annot(ops[0].imm)
            note.append('-> ' + (a[:80] if a else '(sub)'))
            regs = {}
        elif m == 'blx' and len(ops) == 1 and ops[0].type == ARM_OP_REG:
            note.append('(indirect)')
        if struct_reg and len(ops) >= 2 and ops[1].type == ARM_OP_MEM and ins.reg_name(ops[1].mem.base) == struct_reg:
            note.append('%s+0x%x' % (struct_reg, ops[1].mem.disp))
        txt = '%08x  %-10s %-7s %s' % (ins.address, ins.bytes.hex(), m, ins.op_str)
        if note:
            txt += '   ; ' + ' | '.join(note)
        out.append(txt)
    return '\n'.join(out)


if __name__ == '__main__':
    a = int(sys.argv[1], 16)
    b = int(sys.argv[2], 16)
    sr = None
    if '--struct' in sys.argv:
        sr = sys.argv[sys.argv.index('--struct') + 1]
    print(dump(a, b, sr))
