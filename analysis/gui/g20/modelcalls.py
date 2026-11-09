"""Pares (modelo, id) de getModelInfo/requestModelExecute con literales en una .so ARM Thumb (G20). Solo lee."""
import collections
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

sys.path.insert(0, 'scripts/gui')
import elf_scan


def pairs(path):
    d = open(path, 'rb').read(); e = elf_scan.Elf(path); plt = e.plt_map(); md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    want = {a: n for a, n in plt.items() if 'getModelInfo' in n or 'requestModelExecute' in n}
    out = collections.Counter(); regs = {}; pos, hi = 0x1000, len(d) - 4
    while pos < hi:
        got = False
        for i in md.disasm(d[pos:min(hi, pos + 0x10000)], pos):
            got = True; pos = i.address + i.size
            m, o = i.mnemonic, i.op_str; r = o.split(',')[0]
            if m.startswith('ldr') and '[pc' in o and '#' in o:
                lit = ((i.address + 4) & ~3) + int(o.split('#')[1].rstrip(']'), 16)
                if lit + 4 <= len(d): regs[r] = ('lit', struct.unpack_from('<I', d, lit)[0])
            elif m == 'add' and o.endswith(', pc') and regs.get(r, ('',))[0] == 'lit':
                v = (regs[r][1] + i.address + 4) & 0xffffffff
                regs[r] = ('str', d[v:v + 40].split(b'\0')[0].decode('latin1') if v < len(d) else '')
            elif m in ('movs', 'movw', 'mov.w', 'mov') and '#' in o:
                try: regs[r] = ('imm', int(o.split('#')[1], 16))
                except ValueError: pass
            elif m in ('bl', 'blx') and o.startswith('#'):
                t = int(o[1:], 16); n = want.get(t) or want.get(t + 4)
                if n and regs.get('r0', ('',))[0] == 'str' and regs.get('r1', ('',))[0] == 'imm':
                    out[('get' if 'getModelInfo' in n else 'exe', regs['r0'][1], regs['r1'][1])] += 1
                regs = {}
        if not got: pos += 2
    return out


if __name__ == '__main__':
    c = pairs(sys.argv[1]); f = sys.argv[2] if len(sys.argv) > 2 else None
    for (k, n, i), v in sorted(c.items()):
        if not f or f in n: print(k, n, hex(i), v)
