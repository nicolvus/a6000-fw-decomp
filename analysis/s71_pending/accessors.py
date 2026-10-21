"""Accesores de campo del singleton 0x437876dc: funciones `push{r3,lr}; bl 0x437876dc; add r0,#N...; pop`.
Uso: accessors.py [lo hi]  -> lista accesores con desplazamiento en [lo,hi) y sus llamadores."""
import re, sys
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
b = open('analysis/rea-independent/input/av-cam.bin', 'rb').read(); base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
G = '#0x437876dc'
acc = {}
for k, i in enumerate(ins):
    if i.mnemonic == 'bl' and i.op_str == G and k and ins[k-1].mnemonic == 'push':
        off = 0
        for x in ins[k+1:k+4]:
            m = re.match(r'r0, (?:r0, )?#(0x[0-9a-f]+)$', x.op_str)
            if x.mnemonic.startswith('add') and m: off += int(m.group(1), 16)
            elif x.mnemonic == 'pop' or x.mnemonic == 'bx': break
        acc[ins[k-1].address] = off
lo, hi = (int(sys.argv[1], 16), int(sys.argv[2], 16)) if len(sys.argv) > 2 else (0, 1 << 30)
sel = {a: o for a, o in acc.items() if lo <= o < hi}
print(len(acc), 'accesores;', len(sel), 'en rango')
for a, o in sorted(sel.items(), key=lambda t: t[1]):
    callers = [hex(i.address) for i in ins if i.mnemonic in ('bl', 'b.w') and i.op_str == f'#{hex(a)}']
    print(hex(a), hex(o), len(callers), callers[:12])
