"""S55-B: usuarios de las variables de pin inicializadas (GOT -> global). Intérprete lineal por función (lit, add pc, ldr [rb,ro])."""
import sys, re, struct, json, bisect
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from gpio_calls_diff import MODELS, B, disasm
from pin_init import run as init_rows
def users(model):
    d = MODELS[model]['path'].read_bytes(); ins = disasm(d)
    rows = init_rows(model); gv = {r['got']: r for r in rows if r['id'] is not None}
    starts = sorted(i.address for i in ins if i.mnemonic == 'push' and 'lr' in i.op_str) + [1 << 40]
    out = []; R = {}; cur = None
    for x in ins:
        if x.address >= (starts[bisect.bisect_right(starts, x.address) - 1]) and (cur != starts[bisect.bisect_right(starts, x.address) - 1]):
            cur = starts[bisect.bisect_right(starts, x.address) - 1]; R = {}
        op, o = x.mnemonic, x.op_str
        m = re.match(r'(r\d+|sb|sl|ip|fp), (.*)$', o)
        if not m: continue
        rd, rest = m.groups()
        if op.startswith('ldr') and rest.startswith('[pc,'):
            a = ((x.address + 4) & ~3) + int(re.search(r'#(-?0x[0-9a-f]+|\d+)', rest).group(1), 0)
            R[rd] = struct.unpack_from('<I', d, a - B)[0] if 0 <= a - B < len(d) else None
        elif op == 'add' and rest == 'pc' and isinstance(R.get(rd), int): R[rd] = (R[rd] + x.address + 4) & 0xffffffff
        elif op.startswith('ldr') and re.match(r'\[(r\d+), (r\d+)\]$', rest):
            a, b = re.match(r'\[(r\d+), (r\d+)\]$', rest).groups()
            if isinstance(R.get(a), int) and isinstance(R.get(b), int):
                s = (R[a] + R[b]) & 0xffffffff
                if s in gv: out.append(dict(func=cur, at=x.address, var=gv[s]['var'], id=gv[s]['id'])); 
                R[rd] = ('got', s)
            else: R[rd] = None
        elif op in ('mov', 'movs') and rest.startswith('#'): R[rd] = int(rest[1:], 0)
        elif op.startswith(('str', 'cmp', 'tst')): pass
        else: R.pop(rd, None)
    return out
if __name__ == '__main__':
    res = {}
    for m in MODELS:
        u = users(m); res[m] = u
        byf = {}
        for r in u: byf.setdefault(r['func'], set()).add(r['id'])
        print(m, len(u))
        for f, s in sorted(byf.items()): print(f'  {f:#x}', sorted(hex(i) for i in s))
    json.dump(res, open('analysis/s55/var_users.json', 'w'), indent=1)
