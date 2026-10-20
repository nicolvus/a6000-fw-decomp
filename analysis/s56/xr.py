"""S56: índice de llamadas (bl/blx/b.w) y de literales (ldr pc + add pc) de av-cam.bin A6000/A7S.
uso: xr.py MODELO callers 0xFUNC | lit 0xVALOR (valor literal bruto o resuelto)"""
import sys, re, struct, pickle, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 's55'))
from gpio_calls_diff import MODELS, B, disasm
def index(model):
    d = MODELS[model]['path'].read_bytes()
    cache = Path('/tmp/claude-1000/xr-%s-%s.pkl' % (model, hashlib.sha256(d).hexdigest()[:8]))
    if cache.exists(): return d, pickle.load(open(cache, 'rb'))
    ins = disasm(d); calls, lits = {}, []; R = {}
    for i in ins:
        o = i.op_str
        if i.mnemonic in ('bl', 'blx', 'b.w', 'b') and o.startswith('#'): calls.setdefault(int(o[1:], 0), []).append((i.address, i.mnemonic))
        m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', o)
        if i.mnemonic.startswith('ldr') and m:
            la = ((i.address + 4) & ~3) + int(m.group(2), 0)
            if 0 <= la - B < len(d) - 4: v = struct.unpack_from('<I', d, la - B)[0]; R[m.group(1)] = (v, i.address); lits.append((i.address, v, None))
        m = re.match(r'(r\d+), pc$', o)
        if i.mnemonic == 'add' and m and m.group(1) in R:
            v, a0 = R[m.group(1)]; lits.append((a0, v, (v + i.address + 4) & 0xffffffff))
    idx = dict(calls=calls, lits=lits); pickle.dump(idx, open(cache, 'wb')); return d, idx
if __name__ == '__main__':
    d, idx = index(sys.argv[1]); t = int(sys.argv[3], 0)
    if sys.argv[2] == 'callers': [print(hex(a), m) for a, m in idx['calls'].get(t, [])]
    else: [print(hex(a), hex(v), hex(r) if r else '') for a, v, r in idx['lits'] if v == t or r == t]
