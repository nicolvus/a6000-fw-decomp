"""S58: referencias PIC (ldr rN,[pc,#x]; add rN,pc) a direcciones; uso: strrefs.py A7S 0xADDR... ; devuelve instrucciones que referencian y función contenedora aprox (push lr previo)."""
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from tdis import data, B, md, u32, cache
import re, bisect, pickle, os
def sweep(d):
    ins = []; off = 0; n = len(d)
    while off < n:
        got = False
        for i in md.disasm(d[off:], B + off):
            ins.append(i); off = i.address - B + i.size; got = True
        if not got or off < n and not got: off += 2
        elif off < n: off += 2
    return ins
def scan(m):
    cp = cache(f'strrefs_{m}.pkl')
    if os.path.exists(cp): return pickle.load(open(cp, 'rb'))
    d = data(m); ins = sweep(d)
    refs = {}; starts = []
    for k, i in enumerate(ins):
        if i.mnemonic in ('push', 'push.w') and 'lr' in i.op_str: starts.append(i.address)
        mm = re.match(r'(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$', i.op_str)
        if i.mnemonic.startswith('ldr') and mm:
            la = ((i.address + 4) & ~3) + int(mm.group(2), 0)
            if la - B + 4 > len(d): continue
            lit = u32(m, la)
            for j in ins[k + 1:k + 6]:
                if j.mnemonic == 'add' and j.op_str == f'{mm.group(1)}, pc':
                    refs.setdefault((lit + j.address + 4) & 0xffffffff, []).append(i.address); break
    pickle.dump((refs, starts), open(cp, 'wb')); return refs, starts
def func_of(starts, a):
    k = bisect.bisect_right(starts, a) - 1; return starts[k] if k >= 0 else None
if __name__ == '__main__':
    refs, starts = scan(sys.argv[1])
    for target in sys.argv[2:]:
        t = int(target, 0)
        for r in refs.get(t, []): print(hex(t), 'ref at', hex(r), 'func', hex(func_of(starts, r) or 0))
