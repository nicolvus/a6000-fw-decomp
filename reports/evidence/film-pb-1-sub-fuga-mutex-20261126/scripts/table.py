import sys, struct, re, collections, bisect
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import bl_targets, push_entries, cfg, dec

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
LO, HI = 0x6e807c, 0x6ec200
ent = sorted(set(s for s in b.fmap if LO <= s < HI) | bl_targets(LO, HI) | push_entries(LO, HI))
acq = sorted(s for s in b.calls_to(ACQ) if LO <= s < HI)
rel = sorted(s for s in b.calls_to(REL) if LO <= s < HI)

def unit_of(site):
    idx = bisect.bisect_right(ent, site) - 1
    for j in range(idx, -1, -1):
        e = ent[j]
        lim = ent[j + 1] if j + 1 < len(ent) else HI
        ins, _, _, _ = cfg(e, lim)
        if site in ins:
            return e, lim
    return None, None

def lit(i):
    m = re.search(r'\[pc, #(0x[0-9a-f]+)\]', i.op_str)
    if not m:
        return None
    return b.word(((i.address + 4) & ~3) + int(m.group(1), 16))

seen = [0x6e807c]
def method_name(u):
    a, out = u, []
    for _ in range(20):
        i = dec(a)
        if i is None:
            break
        if i.mnemonic == 'bl' and i.op_str.startswith('#0x695c74'):
            break
        if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
            v = lit(i)
            s = b.str_at(v, 48) if v else None
            if s:
                out.append(s)
        a += i.size
    for s in out:
        if s not in ('START', 'END : ', 'mp4Ifo_If.cpp') and not s.startswith('END'):
            return s
    return '?'

print('# method\tunit_start\tunit_end\tacquire_va\tcmd\trelease_va\tline_start')
for s in acq:
    u, lim = unit_of(s)
    rels = [r for r in rel if u <= r < lim]
    # cmd
    cmd = '?'
    a = s - 2
    for _ in range(3):
        i = dec(a)
        if i is None:
            break
        if i.op_str.replace(' ', '').startswith('r1,#'):
            cmd = i.op_str.replace(' ', '')
            break
        a -= i.size
    # source line of the START trace
    line = '?'
    a = u
    for _ in range(12):
        i = dec(a)
        if i is None:
            break
        if i.mnemonic in ('movw', 'mov', 'movs') and i.op_str.replace(' ', '').startswith('r2,#'):
            line = i.op_str.replace(' ', '')
        if i.mnemonic == 'bl' and i.op_str.startswith('#0x695c74'):
            break
        a += i.size
    print('%s\t%08x\t%08x\t%08x\t%s\t%s\t%s' % (method_name(u), u, lim, s, cmd,
          ','.join('%08x' % x for x in rels), line))
