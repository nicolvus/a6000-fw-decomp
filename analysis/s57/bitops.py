"""S57-A/B: mapa estático de operaciones de bits sobre registros sombra IMX210 (región C_Imager 0x436d5000-0x436daa00), por función.
Rastrea ldr de slot GOT -> puntero de registro -> ldrb [ptr,#2] -> orr/bfc/bfi/and -> strb. Aproximado (lineal, sin saltos): complemento de thumbdis."""
import sys, re, struct, json, bisect
sys.path.insert(0, '../s56')
import rec_users as R
from gpio_calls_diff import disasm
B = 0x43541000
s2r = {o: p for p, offs in R.slots.items() for o in offs}
ins = [i for i in disasm(R.d) if 0x436d5000 <= i.address < 0x436daa00]
from common57 import fstarts
starts = fstarts()
def scan():
    out = []
    slot, ptr, val = {}, {}, {}
    for i in ins:
        mn, op = i.mnemonic, i.op_str
        m = re.match(r'(r\d+|sb|sl|ip|lr), \[pc, #(0x[0-9a-f]+|\d+)\]$', op)
        if mn.startswith('ldr') and m:
            la = ((i.address + 4) & ~3) + int(m.group(2), 0); v = struct.unpack_from('<I', R.d, la - B)[0]
            slot[m.group(1)] = s2r.get(v); ptr.pop(m.group(1), None); val.pop(m.group(1), None); continue
        m = re.match(r'(\w+), \[(\w+), (\w+)\]$', op)
        if mn.startswith('ldr') and m and slot.get(m.group(3)):
            ptr[m.group(1)] = slot[m.group(3)]; val.pop(m.group(1), None); continue
        m = re.match(r'(\w+), \[(\w+), #2\]$', op)
        if mn.startswith('ldrb') and m and ptr.get(m.group(2)):
            val[m.group(1)] = ptr[m.group(2)]; continue
        m = re.match(r'(\w+), \[(\w+), #2\]$', op)
        if mn.startswith('strb') and m and ptr.get(m.group(2)):
            out.append((i.address, 'store', R.recs[ptr[m.group(2)]], '')); continue
        m = re.match(r'(\w+), (\w+), #(0x[0-9a-f]+|\d+)$', op)
        if mn.split('.')[0] in ('orr', 'and', 'bic') and m and val.get(m.group(2)):
            val[m.group(1)] = val[m.group(2)]; out.append((i.address, mn.split('.')[0], R.recs[val[m.group(2)]], m.group(3))); continue
        m = re.match(r'(\w+), #(\d+), #(\d+)$', op)
        if mn in ('bfc',) and m and val.get(m.group(1)): out.append((i.address, 'bfc', R.recs[val[m.group(1)]], 'bit%s w%s' % (m.group(2), m.group(3)))); continue
        m = re.match(r'(\w+), (\w+), #(\d+), #(\d+)$', op)
        if mn == 'bfi' and m and val.get(m.group(1)): out.append((i.address, 'bfi', R.recs[val[m.group(1)]], 'bit%s w%s' % (m.group(3), m.group(4)))); continue

    res = {}
    for a, k, rid, arg in out:
        f = starts[bisect.bisect_right(starts, a) - 1]
        res.setdefault(rid, []).append(dict(addr=hex(a), op=k, arg=arg, fn=hex(f)))
    return res
if __name__ == '__main__':
    res = scan()
    json.dump({hex(k): v for k, v in sorted(res.items())}, open('bitops.json', 'w'), indent=0)
    for rid in (1, 0, 0x126, 0x127, 0x128, 0x65, 0x73, 0xdc, 0x12f):
        print(hex(rid), [(x['addr'], x['op'], x['arg']) for x in res.get(rid, [])])
    print('registros con operaciones de bit:', len(res))
