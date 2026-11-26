#!/usr/bin/env python3
"""Desensamblador anotado mínimo para orb-server (ARM32 Thumb-2, ELF EXEC).

- Resuelve símbolos de .dynsym (nombres C++ visibles).
- Resuelve llamadas a .plt -> nombre de la importación (.rel.plt).
- Propaga constantes (movw/movt, add pc, ldr [pc]) para anotar punteros a cadenas.
Solo análisis estático; no modifica el binario.
"""
import struct, subprocess, sys, re
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN
from capstone.arm import ARM_OP_REG, ARM_OP_IMM, ARM_OP_MEM

SECTIONS = {  # name: (vaddr, offset, size)
    '.interp': (0x8134, 0x134, 0x14),
    '.text': (0x183e88, 0x17be88, 0x15f628),
    '.rodata': (0x2e34b8, 0x2db4b8, 0x969ac),
    '.data': (0x39184c, 0x38184c, 0x98c),
    '.bss': (0x3921d8, None, 0x4ca4),
    '.got': (0x39139c, 0x38139c, 0x4b0),
}


def _sections(path):
    out = subprocess.run(['readelf', '-SW', path], capture_output=True, text=True).stdout
    secs = {}
    for line in out.splitlines():
        m = re.match(r'\s*\[\s*\d+\]\s+(\S+)\s+(\S+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)', line)
        if not m:
            continue
        name, typ, addr, off, size = m.groups()
        if typ in ('PROGBITS', 'NOBITS', 'INIT_ARRAY', 'FINI_ARRAY', 'DYNAMIC', 'GOT'):
            secs[name] = (int(addr, 16), None if typ == 'NOBITS' else int(off, 16), int(size, 16))
    return secs


class Bin:
    def __init__(self, path):
        self.path = path
        self.data = open(path, 'rb').read()
        self.SEC = _sections(path)
        self._sym()
        self._plt()
        self.cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB + CS_MODE_LITTLE_ENDIAN)
        self.cs.detail = True

    # --- memoria
    def read(self, vaddr, n):
        for name, (va, off, size) in self.SEC.items():
            if off is None:
                continue
            if va <= vaddr < va + size:
                o = off + (vaddr - va)
                return self.data[o:o + n]
        # otros: convertir con programa headers aproximados (.text/.rodata/.data cubren casi todo el uso)
        return b''

    def cstr(self, vaddr, maxlen=220):
        if vaddr % 2 == 1:
            vaddr -= 1
        b = self.read(vaddr, maxlen)
        if not b or not (32 <= b[0] < 127):
            return None
        s = b.split(b'\x00')[0]
        try:
            t = s.decode('utf-8')
        except Exception:
            return None
        if len(t) < 4:
            return None
        return t

    def _sym(self):
        out = subprocess.run(['readelf', '-sW', self.path], capture_output=True, text=True).stdout
        self.sym = {}
        self.sym_size = {}
        for line in out.splitlines():
            f = line.split()
            if len(f) >= 8 and f[3] in ('FUNC', 'OBJECT') and f[1] != '00000000':
                try:
                    a = int(f[1], 16)
                except ValueError:
                    continue
                if f[4] == 'WEAK' or f[4] == 'GLOBAL':
                    self.sym.setdefault(a & ~1, f[7])
                    self.sym_size[a & ~1] = int(f[2])

    def _plt(self):
        out = subprocess.run(['readelf', '-rW', self.path], capture_output=True, text=True).stdout
        self.plt = {}
        for line in out.splitlines():
            f = line.split()
            if len(f) >= 5 and f[2] == 'R_ARM_JUMP_SLOT':
                addr = int(f[0], 16)
                name = f[4]
                # .plt empieza en 0x18303c, entry 12 bytes: idx = (addr - got) ... se resuelve por el stub
                self.plt[addr] = name
        # mapear direcciones de stubs: cada entrada .plt (12 bytes) acaba en 'add pc, ..., ldr pc,[...]'
        self.plt_addr = {}
        # vía .rel.plt: r_offset es la entrada GOT; la stub i-ésima (i desde 1) usa GOT[i-1]
        got_entries = sorted(self.plt)
        for i, got_addr in enumerate(got_entries):
            self.plt_addr[0x18303c + 12 + 12 * i] = self.plt[got_addr]

    # --- anotaciones
    def annot(self, addr):
        name = None
        if addr in self.sym:
            name = self.sym[addr]
        elif addr & ~1 in self.sym:
            name = self.sym[addr & ~1]
        elif addr in self.plt_addr:
            name = 'plt:' + self.plt_addr[addr]
        s = self.cstr(addr)
        if s:
            s = s.replace('\n', '\\n')
            name = (name + ' | ' if name else '') + '"' + s[:120] + '"'
        return name

    def dis(self, start, end=None, count=None):
        if start % 2 == 1:
            start -= 1
        if end is None:
            end = start + 0x400
        code = self.read(start, end - start)
        regs = {}
        out = []
        for ins in self.cs.disasm(code, start):
            if ins.address >= end:
                break
            txt = f'{ins.address:08x}  {ins.bytes.hex():<10} {ins.mnemonic:<8} {ins.op_str}'
            note = []
            ops = ins.operands
            m = ins.mnemonic
            # constantes: movw/movt
            if m in ('movw', 'movw.w') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
                regs[ins.reg_name(ops[0].reg)] = ops[1].imm & 0xffff if m.startswith('movw') else None
            elif m in ('movt', 'movt.w') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_IMM:
                r = ins.reg_name(ops[0].reg)
                lo = regs.get(r) or 0
                val = ((ops[1].imm & 0xffff) << 16) | lo
                regs[r] = val
                n = self.annot(val)
                if n:
                    note.append('; ' + n)
            elif m in ('add', 'add.w') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_REG and ins.reg_name(ops[1].reg) == 'pc':
                r = ins.reg_name(ops[0].reg)
                base = regs.get(r)
                if base is not None:
                    val = ((ins.address + 4) & ~3) + base
                    regs[r] = val
                    n = self.annot(val)
                    if n:
                        note.append('; ' + n)
            elif m in ('add', 'add.w') and len(ops) >= 3 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_REG:
                a = ins.reg_name(ops[1].reg)
                if a == 'pc' and ops[2].type == ARM_OP_IMM:
                    val = ((ins.address + 4) & ~3) + ops[2].imm
                    r = ins.reg_name(ops[0].reg)
                    regs[r] = val
                    n = self.annot(val)
                    if n:
                        note.append('; ' + n)
                else:
                    base = regs.get(a)
                    if base is not None and ops[2].type == ARM_OP_IMM:
                        val = base + ops[2].imm
                        regs[ins.reg_name(ops[0].reg)] = val
                        n = self.annot(val)
                        if n:
                            note.append('; ' + n)
            elif m.startswith('ldr') and len(ops) == 2 and ops[0].type == ARM_OP_REG and ops[1].type == ARM_OP_MEM and ops[1].mem.base == 15:  # pc
                lit = ((ins.address + 4) & ~3) + ops[1].mem.disp
                val = struct.unpack('<I', self.read(lit, 4) or b'\0\0\0\0')[0]
                regs[ins.reg_name(ops[0].reg)] = val
                n = self.annot(val)
                if n:
                    note.append('; ' + n)
            elif m.startswith('bl') and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
                regs = {}
                n = self.annot(ops[0].imm)
                if n:
                    note.append('; ' + n)
            elif m.startswith('b') and len(ops) == 1 and ops[0].type == ARM_OP_IMM:
                regs = {}
            out.append(txt + ''.join(note))
        return '\n'.join(out)


if __name__ == '__main__':
    b = Bin(sys.argv[1])
    start = int(sys.argv[2], 16)
    end = int(sys.argv[3], 16) if len(sys.argv) > 3 else start + 0x400
    print(b.dis(start, end))
