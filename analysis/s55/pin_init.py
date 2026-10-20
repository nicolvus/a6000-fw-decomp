"""S55-B: inicializador de variables de pin de la tarea CA. Lee la función que hace `Backup_read_4Byte(id); *GOT[off]=r0` y resuelve id -> global."""
import sys, re, struct, json
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
from gpio_calls_diff import MODELS, B, disasm
from bk4 import BK4
R = 'firmware/extracted/'
BKF = {'A6000': R+'fw321/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_ALLLANG.bin',
       'A7S': R+'a7s-fw320/payload/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/ICV/CX78500_ALLLANG.bin'}
WRAP = {'A6000': 0x43561508, 'A7S': 0x4355f7c8}
INIT = {'A6000': 0x436bcef4, 'A7S': 0x436dc054}

def run(model):
    M = MODELS[model]; d = M['path'].read_bytes(); ins = disasm(d); idx = {i.address: k for k, i in enumerate(ins)}
    bk = BK4(BKF[model]); pc4 = lambda a: (a + 4) & ~3
    lit = lambda i: struct.unpack_from('<I', d, pc4(i.address) + int(re.search(r'#(-?0x[0-9a-f]+|\d+)', i.op_str).group(1), 0) - B)[0]
    k = idx[INIT[model]]; regs = {}; rows = []; cur = None; got_base = None
    while True:
        i = ins[k]; op = i.mnemonic
        if op == 'pop' and 'pc' in i.op_str: break
        if op == 'ldr' and '[pc,' in i.op_str:
            regs[i.op_str.split(',')[0]] = lit(i)
        elif op == 'add' and re.match(r'(r\d+), pc$', i.op_str):
            r = i.op_str.split(',')[0]; regs[r] = (regs[r] + i.address + 4) & 0xffffffff; got_base = regs[r]
        elif op == 'bl' and i.op_str == '#%#x' % WRAP[model]:
            cur = regs.get('r0')
        elif op == 'ldr' and re.match(r'(r\d+), \[(r\d+), (r\d+)\]$', i.op_str):
            m = re.match(r'(r\d+), \[(r\d+), (r\d+)\]$', i.op_str)
            off = regs.get(m.group(3))
            if off is not None and got_base is not None:
                g = struct.unpack_from('<I', d, got_base + off - B)[0] if got_base + off - B < len(d) else None
                regs[m.group(1)] = ('got', got_base + off, g)
        elif op == 'str' and re.match(r'r0, \[(r\d+)\]$', i.op_str):
            v = regs.get(re.match(r'r0, \[(r\d+)\]$', i.op_str).group(1))
            if isinstance(v, tuple) and cur is not None:
                rows.append(dict(id=cur, got=v[1], var=v[2], at=i.address)); cur = None
        elif op in ('strb', 'strb.w'):
            v = regs.get(re.match(r'r\d+, \[(r\d+)\]$', i.op_str).group(1)) if re.match(r'r\d+, \[(r\d+)\]$', i.op_str) else None
            if isinstance(v, tuple): rows.append(dict(id=None, got=v[1], var=v[2], at=i.address, const=i.op_str))
        k += 1
    for r in rows:
        if r['id'] is not None:
            e = bk.entry(r['id']); r['value'] = None if e is None else (lambda x: None if x == 0xffffffff else x)(bk.u32(bk.ptr(r['id'])))
    return rows

if __name__ == '__main__':
    out = {}
    for m in MODELS:
        rows = run(m); out[m] = rows
        print(m, len(rows))
        for r in rows: print(f"  id={r['id'] and hex(r['id'])} -> var {r['var'] and hex(r['var'])} (GOT {r['got']:#x}) value={r.get('value')} @ {r['at']:#x} {r.get('const','')}")
    json.dump(out, open('analysis/s55/pin_init.json', 'w'), indent=1)
