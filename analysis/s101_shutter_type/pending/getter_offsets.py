"""Usos de un getter-singleton con desplazamientos en [lo,hi).
Uso: getter_offsets.py GETTER lo hi [ventana]  (p.ej. 437876dc dd0 df0 40)"""
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

b = Path('analysis/rea-independent/input/av-cam.bin').read_bytes(); base = 0x43541000
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
ins = list(md.disasm(b[:0x9c0000], base))
G = f'#0x{sys.argv[1]}'; lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
W = int(sys.argv[4]) if len(sys.argv) > 4 else 40
n = 0
for k, i in enumerate(ins):
    if i.mnemonic == 'bl' and i.op_str == G:
        n += 1; regs = {'r0'}
        for j in ins[k+1:k+W]:
            o = j.op_str
            if j.mnemonic in ('pop', 'pop.w') and 'pc' in o: break
            m = re.match(r'(\w+), (\w+)$', o)
            if j.mnemonic.startswith('mov') and m:
                (regs.add if m.group(2) in regs else regs.discard)(m.group(1))
            for imm in re.findall(r'#(0x[0-9a-f]+)', o):
                v = int(imm, 16)
                if lo <= v < hi and any(re.search(rf'\b{r}\b', o) for r in regs):
                    print(hex(i.address), hex(j.address), j.mnemonic, o)
            if j.mnemonic == 'bl': regs.discard('r0')
print(n, 'llamadas al getter')
