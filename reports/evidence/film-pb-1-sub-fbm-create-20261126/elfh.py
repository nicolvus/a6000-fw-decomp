"""Generic ELF32 ARM helper for the Sony A6000 firmware libraries (fw 3.21).

Usage: python3 elfhelper.py <lib.so> dis <va> <len>
       python3 elfhelper.py <lib.so> sym <substr>
       python3 elfhelper.py <lib.so> str <substr>
       python3 elfhelper.py <lib.so> xref <va>
       python3 elfhelper.py <lib.so> calls <target_va>
"""
import struct
import sys
from capstone import *


class Elf:
    def __init__(self, path):
        self.path = path
        self.d = open(path, 'rb').read()
        d = self.d
        e_phoff = struct.unpack_from('<I', d, 28)[0]
        e_phentsize = struct.unpack_from('<H', d, 42)[0]
        e_phnum = struct.unpack_from('<H', d, 44)[0]
        self.segs = []
        for i in range(e_phnum):
            o = e_phoff + i * e_phentsize
            t, off, va, pa, fsz, msz, fl, al = struct.unpack_from('<8I', d, o)
            if t == 1:
                self.segs.append((off, va, fsz))
        e_shoff = struct.unpack_from('<I', d, 32)[0]
        e_shentsize = struct.unpack_from('<H', d, 46)[0]
        e_shnum = struct.unpack_from('<H', d, 48)[0]
        e_shstrndx = struct.unpack_from('<H', d, 50)[0]
        secs = []
        for i in range(e_shnum):
            o = e_shoff + i * e_shentsize
            secs.append(struct.unpack_from('<10I', d, o))
        shstr = secs[e_shstrndx]
        self.sec = {}
        for s in secs:
            o = shstr[4] + s[0]
            nm = d[o:d.index(b'\0', o)].decode()
            self.sec[nm] = (s[3], s[4], s[5])
        self.syms = []
        dyn = self.sec.get('.dynsym')
        if dyn:
            addr, off, size = dyn
            strtab_addr, strtab_off, strtab_size = self.sec['.dynstr']
            for i in range(size // 16):
                o = off + i * 16
                name, value, sz, info, other, shndx = struct.unpack_from('<IIIBBH', d, o)
                e = d.index(b'\0', strtab_off + name)
                self.syms.append((value, sz, info & 0xf, info >> 4,
                                  d[strtab_off + name:e].decode('latin1')))
        self.plt = {}
        self.plt_got = {}
        if '.rel.plt' in self.sec and '.plt' in self.sec:
            _, reloff, relsize = self.sec['.rel.plt']
            ents = self._plt_entries()
            for i, a in enumerate(ents):
                if i * 8 + 8 <= relsize:
                    o = reloff + i * 8
                    r_off, r_info = struct.unpack_from('<II', d, o)
                    if (r_info >> 8) < len(self.syms):
                        self.plt[a] = self.syms[r_info >> 8][4]
                        self.plt_got[a] = r_off

    def _plt_entries(self):
        va, off, size = self.sec['.plt']
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        return [x.address for x in md.disasm(self.d[off:off + size], va)
                if x.mnemonic == 'add' and x.op_str.replace(' ', '').startswith('ip,pc')]

    def read(self, va, n):
        for po, base, fsz in self.segs:
            if base <= va < base + fsz:
                o = po + va - base
                return self.d[o:min(o + n, po + fsz)]
        return b''

    def va2off(self, va):
        for po, base, fsz in self.segs:
            if base <= va < base + fsz:
                return po + va - base
        return None

    def off2va(self, off):
        for po, base, fsz in self.segs:
            if po <= off < po + fsz:
                return base + off - po
        return None

    def name_at(self, addr):
        best = None
        for v, s, t, b, n in self.syms:
            if t in (1, 2) and v:
                a = v & ~1
                if a <= addr and (s == 0 or addr < a + s):
                    if best is None or a > best[0]:
                        best = (a, n, s)
        if best:
            return best[1] + ('+0x%x' % (addr - best[0]) if addr != best[0] else '')
        return None

    def dis(self, va, n):
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        for i in md.disasm(self.read(va, n), va):
            extra = ''
            ops = i.op_str.replace(' ', '')
            if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
                import re
                m = re.search(r'#(0x[0-9a-f]+)', i.op_str)
                if m:
                    tgt = ((i.address + 4) & ~3) + int(m.group(1), 16)
                    val = self.read(tgt, 4)
                    if len(val) == 4:
                        num = struct.unpack('<I', val)[0]
                        note = ''
                        s = self.read(num, 40)
                        if s and all(32 <= c < 127 or c in (9, 10) for c in s.split(b'\0')[0]) and len(s.split(b'\0')[0]) > 3:
                            note = ' "' + s.split(b'\0')[0].decode('latin1')[:40] + '"'
                        extra = '  ; [%08x]=%08x%s' % (tgt, num, note)
            if i.mnemonic in ('bl', 'blx') and ops.startswith('#'):
                import re
                m = re.search(r'#(0x[0-9a-f]+)', i.op_str)
                if m:
                    tgt = int(m.group(1), 16)
                    nm = self.plt.get(tgt) or self.name_at(tgt)
                    if nm:
                        extra = '  ; ' + nm
            print('%08x: %-10s %-8s %-30s%s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str, extra))

    def strings(self, sub):
        d = self.d
        out = []
        s = 0
        while True:
            i = d.find(sub.encode(), s)
            if i < 0:
                break
            a = d.rfind(b'\0', 0, i) + 1
            b = d.index(b'\0', i)
            va = self.off2va(a)
            out.append((va, d[a:b].decode('latin1')))
            s = i + 1
        return out

    def xrefs(self, target):
        """Literals (u32) equal to target anywhere; returns referencing addresses."""
        pat = struct.pack('<I', target)
        out = []
        i = 0
        d = self.d
        while True:
            i = d.find(pat, i)
            if i < 0:
                break
            out.append(self.off2va(i))
            i += 1
        return out

    def calls(self, target):
        text_va, text_off, text_sz = self.sec['.text']
        out = []
        d = self.d
        for off in range(text_off, text_off + text_sz - 3, 2):
            hw1, hw2 = struct.unpack_from('<HH', d, off)
            if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xC000) != 0xC000:
                continue
            s = (hw1 >> 10) & 1
            imm10 = hw1 & 0x3FF
            j1 = (hw2 >> 13) & 1
            j2 = (hw2 >> 11) & 1
            imm11 = hw2 & 0x7FF
            i1 = (~(j1 ^ s)) & 1
            i2 = (~(j2 ^ s)) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if s:
                imm -= 1 << 25
            pc = text_va + (off - text_off)
            if pc + 4 + imm == target:
                out.append(pc)
        return out


if __name__ == '__main__':
    e = Elf(sys.argv[1])
    cmd = sys.argv[2]
    if cmd == 'dis':
        e.dis(int(sys.argv[3], 16), int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x80)
    elif cmd == 'sym':
        for v, s, t, b, n in sorted(e.syms):
            if sys.argv[3].lower() in n.lower():
                print('%08x %6d %s' % (v & ~1, s, n))
    elif cmd == 'str':
        for va, s in e.strings(sys.argv[3]):
            print(hex(va) if va else '?', s)
    elif cmd == 'xref':
        for a in e.xrefs(int(sys.argv[3], 16)):
            print(hex(a) if a else '?', e.name_at(a) if a else '')
    elif cmd == 'calls':
        for a in e.calls(int(sys.argv[3], 16)):
            print(hex(a), e.name_at(a))
