import sys, struct, re, collections, bisect
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import cfg, exits, bl_targets, push_entries, dec, success_entries

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
LO, HI = 0x6e807c, 0x6ec200

ent = sorted(set(s for s in b.fmap if LO <= s < HI) | bl_targets(LO, HI) | push_entries(LO, HI))
acq = [s for s in b.calls_to(ACQ) if LO <= s < HI]
rel = [s for s in b.calls_to(REL) if LO <= s < HI]

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
    """literal value for ldr rX,[pc,#imm]"""
    m = re.search(r'\[pc, #(0x[0-9a-f]+)\]', i.op_str)
    if not m:
        return None
    tgt = ((i.address + 4) & ~3) + int(m.group(1), 16)
    return b.word(tgt)

def method_name(u):
    a = u
    seen = []
    for k in range(20):
        i = dec(a)
        if i is None:
            break
        if i.mnemonic == 'bl' and i.op_str.startswith('#0x695c74'):
            break
        if i.mnemonic.startswith('ldr') and '[pc' in i.op_str:
            v = lit(i)
            if v:
                s = b.str_at(v, 48)
                if s:
                    seen.append(s)
        a += i.size
    for s in seen:
        if s not in ('START', 'END : ', 'mp4Ifo_If.cpp') and not s.startswith('END'):
            return s
    return '?'

def cmd_of(site):
    i = dec(site - 4)
    j = dec(site - 2)
    for x in (j, i):
        if x and x.mnemonic in ('movs', 'mov', 'mov.w', 'movw') and x.op_str.replace(' ', '').startswith('r1,#'):
            return x.op_str.replace(' ', '')
    return '?'

rows = []
for s in acq:
    u, lim = unit_of(s)
    rels = [r for r in rel if u is not None and u <= r < lim]
    starts, how = success_entries(s)
    ins, edges, kind, call = cfg(u, lim) if u is not None else ({}, {}, {}, {})
    ex = exits(u, lim) if u is not None else set()
    prev, q, hits = {}, collections.deque(), []
    for x in starts:
        prev[x] = None
        q.append(x)
    while q:
        a = q.popleft()
        if a in ex:
            hits.append(a)
            continue
        for kk, t in edges.get(a, []):
            if not (u <= t < lim):
                hits.append(a)
                continue
            if t in rels or t in prev:
                continue
            prev[t] = a
            q.append(t)
    rows.append({'acq': s, 'rel': rels, 'unit': u, 'lim': lim, 'name': method_name(u) if u else '?',
                 'cmd': cmd_of(s), 'hits': hits, 'how': how, 'prev': prev})

leaks = [r for r in rows if r['hits']]
print('acquire sites analysed:', len(rows))
print('leaky:', len(leaks))
for r in rows:
    print('%08x  acq=%08x %-8s rel=%-22s %-26s %s' % (
        r['unit'], r['acq'], r['cmd'], ','.join('%x' % x for x in r['rel']) or '-',
        r['name'], 'LEAK:' + ','.join('%x' % h for h in r['hits']) if r['hits'] else 'OK'))
print()
for r in leaks:
    for h in r['hits'][:4]:
        path, cur = [], h
        while cur is not None:
            path.append(cur)
            cur = r['prev'].get(cur)
        print('%08x exit %x :' % (r['acq'], h), ' <- '.join('%x' % x for x in path[:16]))
