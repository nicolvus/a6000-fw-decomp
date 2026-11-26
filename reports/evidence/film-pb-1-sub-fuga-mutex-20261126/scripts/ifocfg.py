import sys, struct, re, bisect, collections
sys.path.insert(0, '/tmp')
from ifotool import Binary
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
COND_B = re.compile(r'^b(eq|ne|cs|cc|hs|lo|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)$')

def dec(a):
    for i in md.disasm(b.read(a, 4), a):
        return i
    return None

def succ(i):
    m, ops = i.mnemonic, i.op_str.replace(' ', '')
    nxt = i.address + i.size
    if m == 'b':
        return [('j', int(ops.lstrip('#'), 16))], 'ub'
    if COND_B.match(m) or m in ('cbz', 'cbnz'):
        t = [int(x.lstrip('#'), 16) for x in ops.split(',') if x.startswith('#0x')]
        return ([('f', nxt)] + ([('c', t[-1])] if t else [])), 'cond'
    if m in ('bl', 'blx'):
        return [('f', nxt)], 'call'
    if m == 'bx':
        return [], 'ret'
    if m == 'pop' and 'pc' in ops:
        return [], 'ret'
    if m in ('tbb', 'tbh'):
        return [], 'ret'
    if m in ('ldr', 'ldrb', 'ldrh') and ops.startswith('pc,'):
        return [], 'ret'
    if m == 'add' and ops.startswith('pc,pc'):
        return [], 'ret'
    return [('f', nxt)], 'seq'

CACHE = {}

def cfg(entry, limit):
    key = (entry, limit)
    if key in CACHE:
        return CACHE[key]
    ins, edges, kind, call = {}, {}, {}, {}
    wl = [entry]
    while wl:
        a = wl.pop()
        while True:
            if a in ins or not (entry <= a < limit):
                break
            i = dec(a)
            if i is None:
                break
            ins[a] = i
            s, k = succ(i)
            edges[a], kind[a] = s, k
            if k == 'call':
                call[a] = int(i.op_str.lstrip('#'), 16) if i.mnemonic == 'bl' else None
            if k == 'ret':
                break
            if k == 'ub':
                t = s[0][1]
                if entry <= t < limit:
                    a = t
                    continue
                break
            nxt = None
            for kk, t in s:
                if kk in ('c', 'j') and entry <= t < limit and t not in ins:
                    wl.append(t)
                if kk == 'f':
                    nxt = t
            if nxt is None:
                break
            a = nxt
    CACHE[key] = (ins, edges, kind, call)
    return CACHE[key]

def exits(entry, limit):
    ins, edges, kind, _ = cfg(entry, limit)
    out = set()
    for a in ins:
        k = kind[a]
        if k == 'ret':
            out.add(a)
        elif k == 'ub' and not (entry <= edges[a][0][1] < limit):
            out.add(a)
    return out

def bl_targets(lo, hi):
    out = set()
    va, off, sz = b.text_va, b.text_off, b.text_sz
    d = b.d
    for o in range(off, off + sz - 3, 2):
        hw1, hw2 = struct.unpack_from('<HH', d, o)
        if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xC000) != 0xC000:
            continue
        s = (hw1 >> 10) & 1
        imm10 = hw1 & 0x3FF
        j1 = (hw2 >> 13) & 1
        j2 = (hw2 >> 11) & 1
        imm11 = hw2 & 0x7FF
        i1 = (~(j1 ^ s)) & 1
        i2 = (~(j2 ^ s)) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            imm -= 1 << 25
        t = va + (o - off) + 4 + imm
        if lo <= t < hi:
            out.add(t)
    return out

def success_entries(site):
    """given acquire callsite, return list of addresses on the 'acquired' path"""
    i = dec(site + 4)
    if i is None:
        return [], 'noins'
    m, ops = i.mnemonic, i.op_str.replace(' ', '')
    nxt = i.address + i.size
    tgts = [int(x.lstrip('#'), 16) for x in ops.split(',') if x.startswith('#0x')]
    if m == 'cbz' and ops.startswith('r0'):
        return ([tgts[-1]] if tgts else []), 'cbz'
    if m == 'cbnz' and ops.startswith('r0'):
        return [nxt], 'cbnz'
    if m in ('cmp', 'cmp.w') and ops.startswith('r0,#0'):
        j = dec(nxt)
        if j and j.mnemonic in ('beq', 'beq.w'):
            return ([int(j.op_str.lstrip('#'), 16)], 'cmp/beq')
        if j and j.mnemonic in ('bne', 'bne.w'):
            return [nxt + j.size], 'cmp/bne'
    if m in ('cbz', 'cbnz'):
        return ([tgts[-1]] if m == 'cbz' else [nxt]), 'other-reg-' + m
    if m in ('str', 'str.w') or m.startswith('st'):
        return [nxt], 'store-result'
    return [nxt], 'unknown:' + m

def analyze(lo, hi, quiet=False, verbose=False):
    ent = set(s for s in b.fmap if lo <= s < hi) | bl_targets(lo, hi)
    ent = sorted(ent)
    acq = [s for s in b.calls_to(ACQ) if lo <= s < hi]
    rel = [s for s in b.calls_to(REL) if lo <= s < hi]
    res = []
    for site in acq:
        idx = bisect.bisect_right(ent, site) - 1
        unit = None
        for j in range(idx, -1, -1):
            e = ent[j]
            lim = ent[j + 1] if j + 1 < len(ent) else hi
            ins, _, _, _ = cfg(e, lim)
            if site in ins:
                unit = (e, lim)
                break
        if unit is None:
            res.append({'site': site, 'tag': 'NO-UNIT'})
            continue
        e, lim = unit
        ins, edges, kind, call = cfg(e, lim)
        ex = exits(e, lim)
        rels = [r for r in rel if e <= r < lim]
        starts, how = success_entries(site)
        prev = {}
        q = collections.deque()
        for s in starts:
            prev[s] = None
            q.append(s)
        hits = []
        needrel = []
        while q:
            a = q.popleft()
            if a in ex:
                hits.append(a)
                continue
            if a not in ins and e <= a < lim:
                # decode stray
                pass
            for kk, t in edges.get(a, []):
                if not (e <= t < lim):
                    hits.append(a)
                    continue
                if t in rels or t in prev:
                    continue
                prev[t] = a
                q.append(t)
        tag = 'LEAK' if hits else 'OK'
        if how.startswith('unknown') or how.startswith('other'):
            tag += '?(' + how + ')'
        res.append({'site': site, 'unit': e, 'lim': lim, 'rels': rels, 'tag': tag,
                    'hits': hits, 'prev': prev, 'how': how})
        if not quiet:
            print('%08x  %s  rel=%s  %s' % (site, tag, ','.join('%x' % x for x in rels) or '-', how))
            if hits and verbose:
                for h in hits[:3]:
                    path, cur = [], h
                    while cur is not None:
                        path.append(cur)
                        cur = prev.get(cur)
                    print('     exit %x :' % h, ' <- '.join('%x' % x for x in path[:16]))
    return res

def push_entries(lo, hi):
    out = set()
    a = lo
    while a < hi:
        i = dec(a)
        if i is None:
            a += 2
            continue
        if i.mnemonic in ('push', 'push.w') and ('lr' in i.op_str):
            out.add(a)
        a += i.size
    return out
