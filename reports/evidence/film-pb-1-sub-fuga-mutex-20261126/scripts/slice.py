import sys, struct, re, bisect, collections
sys.path.insert(0, '/tmp')
from ifotool import Binary
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

def dec(a):
    for i in md.disasm(b.read(a, 4), a):
        return i
    return None

def func_ins(start, end, limit=4000):
    """linear disassembly (no CFG) of the whole unit; may include literal pools"""
    out = []
    a = start
    while a < end and len(out) < limit:
        i = dec(a)
        if i is None:
            break
        out.append(i)
        a += i.size
    return out

WRITE1 = re.compile(r'^(ldr|ldrb|ldrh|ldrsb|ldrsh|mov|movs|add|adds|sub|subs|adr|and|orr|eor|mvn|mvns|lsl|lsr|asr|ldrd|str|strb)$')

def dst_ops(i):
    if not i.op_str:
        return None, i.op_str
    parts = i.op_str.split(',')
    return parts[0].strip(), ','.join(parts[1:]).strip()

def track(ins_list, site, reg='r0', hops=6, depth=0):
    """find the definition of reg before site; returns chain list of (addr, mnemonic, op_str)"""
    idx = None
    for k, i in enumerate(ins_list):
        if i.address >= site:
            idx = k
            break
    if idx is None:
        idx = len(ins_list)
    chain = []
    cur = reg
    # single hop walk
    for i in reversed(ins_list[max(0, idx - 60):idx]):
        d, s = dst_ops(i)
        if d != cur:
            # handle 'ldr r0, [r1]' where op_str first token is dest. also 'ldrd r0,r1'
            continue
        chain.append((i.address, i.mnemonic, i.op_str))
        m = i.mnemonic
        if m in ('ldr', 'ldrb', 'ldrh', 'ldrsb', 'ldrsh', 'ldrd') and s.startswith('['):
            base = s.split(',')[0].strip('[').strip()
            off = ''
            if ',' in s:
                off = s.split(',')[1].strip().rstrip(']')
            return {'kind': 'load', 'base': base, 'off': off, 'at': i.address, 'chain': chain}
        if m in ('mov', 'movs') and s:
            src = s.split(',')[0].strip()
            if src in ('r0','r1','r2','r3','r4','r5','r6','r7','r8','r9','r10','r11','r12','sb','sl','fp','ip'):
                cur = src
                if depth < hops:
                    return track(ins_list, i.address, src, hops, depth + 1)
                return {'kind': 'movreg', 'chain': chain}
            return {'kind': 'movimm', 'val': src, 'at': i.address, 'chain': chain}
        return {'kind': m, 'ops': i.op_str, 'at': i.address, 'chain': chain}
    return {'kind': 'entry-' + cur, 'at': None, 'chain': chain}

def provenance(site):
    f = b.func_at(site)
    start, end = f
    ins = func_ins(start, end)
    p = track(ins, site, 'r0')
    return start, p

if __name__ == '__main__':
    lo, hi = (int(sys.argv[1], 16), int(sys.argv[2], 16)) if len(sys.argv) > 2 else (b.text_va, b.text_va + b.text_sz)
    acq = [s for s in b.calls_to(ACQ) if lo <= s < hi]
    rel = [s for s in b.calls_to(REL) if lo <= s < hi]
    kinds = collections.Counter()
    rows = []
    for s in acq:
        try:
            st, p = provenance(s)
        except Exception as ex:
            rows.append((s, None, {'kind': 'ERR ' + str(ex)}))
            continue
        k = p['kind'] + (':' + p.get('off', '') if p['kind'] == 'load' else '')
        kinds[k] += 1
        rows.append((s, st, p))
    print('acquire sites:', len(acq), 'release:', len(rel))
    for k, v in kinds.most_common():
        print('  %-22s %d' % (k, v))
    print()
    for s, st, p in rows:
        if p['kind'] == 'load' and p.get('off') not in ('#4', ''):
            print('%08x unit=%08x base=%s off=%s' % (s, st, p['base'], p['off']))
