#!/usr/bin/env python3
"""fdiff.py A7S_START A7S_END A6000_START A6000_END [-v]
Alinea (difflib) dos rangos del desensamblado lineal LLVM, normalizando destinos de salto/bl y literales PC,
y lista las instrucciones A7S insertadas/reemplazadas (no presentes en A6000). Offsets de captura sin normalizar."""
import difflib
import re
import sys
from pathlib import Path

D = '/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/work/claude/s52/dis/'
def load(f, s, e):
    out = []
    for l in Path(D + f).read_text().splitlines():
        m = re.match(r'([0-9a-f]{8}):\s+(\S+)\s*(.*)', l)
        if not m: continue
        a = int(m.group(1), 16)
        if a < s: continue
        if a >= e: break
        op, arg = m.group(2), re.sub(r'\s*<_binary[^>]*>', '', m.group(3))
        n = re.sub(r'@.*', '', arg)
        if op.startswith(('b', 'cb')) and not op.startswith(('bic', 'bfi', 'bfc')): n = re.sub(r'0x[0-9a-f]{8}', 'T', n)
        if 'pc' in n and op.startswith('ldr'): n = re.sub(r'#0x[0-9a-f]+', '#L', n)
        out.append((a, op + ' ' + n.strip(), op + ' ' + arg.strip()))
    return out
s7, e7, s6, e6 = (int(x, 16) for x in sys.argv[1:5])
A, B = load('a7s.dis', s7, e7), load('a6000.dis', s6, e6)
sm = difflib.SequenceMatcher(None, [x[1] for x in B], [x[1] for x in A], autojunk=False)
print(f'ratio={sm.ratio():.3f}')
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal': continue
    print(f'-- {tag} A6000[{B[i1][0] if i1 < len(B) else 0:#x}+{i2-i1}] A7S[{A[j1][0] if j1 < len(A) else 0:#x}+{j2-j1}]')
    if '-v' in sys.argv or tag != 'equal':
        for x in B[i1:i2][:12]: print(f'   6 {x[0]:x}: {x[2]}')
        for x in A[j1:j2][:12]: print(f'   7 {x[0]:x}: {x[2]}')
