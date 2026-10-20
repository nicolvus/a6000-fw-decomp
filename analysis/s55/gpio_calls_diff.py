"""S55: sitios de llamada a gpio_get/cfg/set en av-cam.bin de A6000 y A7S, con origen de r0/r1 (inmediato, literal o global)."""
import re, json, struct, hashlib
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
ROOT = Path(__file__).resolve().parents[2]
P = 'firmware/extracted/%s/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin'
MODELS = {
    'A6000': dict(path=ROOT/(P % 'fw321/firmware.tar_unpacked'), get=0x43b5e2bc, cfg=0x43b5e22e, set=0x43b5e29a),
    'A7S':   dict(path=ROOT/(P % 'a7s-fw320/payload/firmware.tar_unpacked'), get=0x43b585c2, cfg=0x43b58534, set=0x43b585a0),
}
B = 0x43541000
BR = ('b', 'bl', 'blx', 'bx', 'cbz', 'cbnz', 'pop', 'tbb', 'tbh')

_CACHE = {}
def disasm(d):
    # caché por SHA: el desensamblado lineal del blob tarda ~40 s
    key = hashlib.sha256(d).hexdigest()
    if key not in _CACHE:
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.detail = False; md.skipdata = True
        _CACHE[key] = [i for i in md.disasm(d[:0x43fe0000 - B], B) if i.mnemonic != '.byte']
    return _CACHE[key]

def lit(d, i):
    m = re.match(r'(r\d+), \[pc, #(-?0x[0-9a-f]+|-?\d+)\]$', i.op_str)
    if not m: return None
    a = ((i.address + 4) & ~3) + int(m.group(2), 0)
    return m.group(1), struct.unpack_from('<I', d, a - B)[0], a

def origin(d, ins, k, reg):
    """Busca hacia atrás (dentro del bloque) cómo se define `reg` justo antes de ins[k]."""
    for j in range(k - 1, max(k - 24, 0), -1):
        i = ins[j]; op, o = i.mnemonic, i.op_str
        if op.split('.')[0] in BR and not (op == 'bl'): return 'unknown(branch)'
        if op == 'bl' and reg in ('r0',): return f'ret@{i.address:#x}'
        if op == 'bl': 
            if reg in ('r4', 'r5', 'r6', 'r7', 'r8'): continue
            return 'clobbered(bl)'
        m = re.match(r'%s, #(0x[0-9a-f]+|\d+)$' % reg, o)
        if m and op in ('movs', 'mov', 'mov.w', 'movw', 'mvn'): return f'imm {int(m.group(1), 0)}'
        m = re.match(r'%s, (r\d+)$' % reg, o)
        if m and op in ('mov', 'movs'): return origin(d, ins, j, m.group(1)) + f' via {m.group(1)}'
        m = lit(d, i)
        if m and m[0] == reg: return f'lit {m[1]:#x}@{m[2]:#x}'
        m = re.match(r'%s, \[(r\d+)(?:, #(0x[0-9a-f]+|\d+))?\]$' % reg, o)
        if m and op.startswith('ldr'):
            src = origin(d, ins, j, m.group(1)); return f'[{src}+{m.group(2) or 0}]'
        m = re.match(r'%s, ' % reg, o)
        if m and not op.startswith(('str', 'cmp', 'tst', 'push')): return f'computed({op} {o})'
    return 'unknown'

def scan(name):
    M = MODELS[name]; d = M['path'].read_bytes(); ins = disasm(d)
    tg = {M[k]: k for k in ('get', 'cfg', 'set')}
    starts = sorted(i.address for i in ins if i.mnemonic == 'push' and 'lr' in i.op_str)
    import bisect
    out = []
    for k, i in enumerate(ins):
        if i.mnemonic in ('bl', 'b.w', 'blx') and i.op_str.startswith('#'):
            t = int(i.op_str[1:], 16)
            if t in tg:
                f = starts[bisect.bisect_right(starts, i.address) - 1]
                out.append(dict(addr=i.address, kind=tg[t], func=f, tail=i.mnemonic != 'bl',
                                r0=origin(d, ins, k, 'r0'), r1=origin(d, ins, k, 'r1')))
    return dict(sha256=hashlib.sha256(d).hexdigest(), sites=out)

if __name__ == '__main__':
    res = {n: scan(n) for n in MODELS}
    Path(ROOT/'analysis/s55/gpio_calls_diff.json').write_text(json.dumps(res, indent=1))
    for n, r in res.items():
        from collections import Counter
        print(n, r['sha256'][:12], len(r['sites']), Counter(s['kind'] for s in r['sites']))
