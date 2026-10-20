"""S55: resuelve (canal,bit) de cada llamada a gpio_get/set/cfg con un intérprete lineal mínimo desde el inicio de la función.
Fuentes: IDs de backup (Backup_read_4Byte), variables globales inicializadas por pin_init, inmediatos. Resultado marcado 'lin' (lineal: sin ramas)."""
import re, sys, json, struct, bisect
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from gpio_calls_diff import MODELS, B, disasm
from bk4 import BK4
from pin_init import BKF, run as init_rows
UNK = None
def pin_value(bk, id_):
    e = bk.entry(id_)
    if e is None: return 'noentry'
    v = bk.u32(bk.ptr(id_)); return 'unset' if v == 0xffffffff else v

def resolve(model):
    M = MODELS[model]; d = M['path'].read_bytes(); ins = disasm(d); bk = BK4(BKF[model])
    var = {r['var']: r for r in init_rows(model) if r['id'] is not None}      # global -> id/valor
    starts = sorted(i.address for i in ins if i.mnemonic == 'push' and 'lr' in i.op_str)
    idx = {i.address: k for k, i in enumerate(ins)}
    tg = {M[k]: k for k in ('get', 'cfg', 'set')}
    out = []
    rd = lambda a, n=4: d[a - B:a - B + n] if 0 <= a - B < len(d) else None
    for k, i in enumerate(ins):
        if not (i.mnemonic in ('bl', 'b.w') and i.op_str.startswith('#') and int(i.op_str[1:], 16) in tg): continue
        t = tg[int(i.op_str[1:], 16)]; f = starts[bisect.bisect_right(starts, i.address) - 1]
        R = {}; kk = idx[f]; lastret = None
        while kk < k:
            x = ins[kk]; op, o = x.mnemonic, x.op_str; kk += 1
            m = re.match(r'(r\d+|sb|sl|ip|fp), (.*)$', o)
            if not m: 
                if op == 'bl' or op == 'blx': R = {r: v for r, v in R.items() if r not in ('r0', 'r1', 'r2', 'r3', 'ip')}; R['r0'] = ('ret', x.address)
                continue
            rdst, rest = m.group(1), m.group(2)
            try:
                if op.startswith('ldr') and rest.startswith('[pc,'):
                    a = ((x.address + 4) & ~3) + int(re.search(r'#(-?0x[0-9a-f]+|\d+)', rest).group(1), 0); R[rdst] = ('v', struct.unpack_from('<I', d, a - B)[0])
                elif op == 'add' and rest == 'pc': R[rdst] = ('v', (R[rdst][1] + x.address + 4) & 0xffffffff)
                elif op in ('mov', 'movs') and rest.startswith('#'): R[rdst] = ('v', int(rest[1:], 0))
                elif op in ('mov', 'movs') and re.match(r'r\d+$', rest): R[rdst] = R.get(rest)
                elif op.startswith('ldr') and re.match(r'\[(r\d+), (r\d+)\]$', rest):
                    a, b = re.match(r'\[(r\d+), (r\d+)\]$', rest).groups()
                    if R.get(a) and R.get(b): R[rdst] = ('mem', R[a][1] + R[b][1], struct.unpack_from('<I', d, R[a][1] + R[b][1] - B)[0])  # entrada GOT
                    else: R[rdst] = None
                elif op.startswith('ldr') and re.match(r'\[(r\d+)\]$', rest):
                    a = re.match(r'\[(r\d+)\]$', rest).group(1); v = R.get(a)
                    R[rdst] = ('val', v[2]) if v and v[0] == 'mem' else None
                elif op.startswith('ldr') and re.match(r'\[(r\d+), #(0x[0-9a-f]+|\d+)\]$', rest): R[rdst] = None
                elif op in ('str', 'strb', 'strh', 'cmp', 'tst', 'cmn') : pass
                else: R[rdst] = None
            except Exception: R[rdst] = None
        def val(r):
            v = R.get(r)
            if v is None: return '?'
            if v[0] == 'v': return v[1]
            if v[0] == 'val':
                g = var.get(v[1]); return ('var %#x=%s' % (v[1], pin_value(bk, g['id']) if g else '?'))
            if v[0] == 'ret': return 'ret@%#x' % v[1]
            return '?'
        out.append(dict(addr=i.address, kind=t, func=f, r0=val('r0'), r1=val('r1'), method='lin'))
    return out
if __name__ == '__main__':
    res = {m: resolve(m) for m in MODELS}
    json.dump(res, open('analysis/s55/pin_resolve.json', 'w'), indent=1)
    for m, rows in res.items():
        print(m)
        for r in rows:
            if isinstance(r['r0'], str) and r['r0'].startswith('var'): print(f"  {r['addr']:#x} {r['kind']} f={r['func']:#x} {r['r0']} | {r['r1']}")
