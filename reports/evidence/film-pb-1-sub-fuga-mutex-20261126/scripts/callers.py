import sys, struct, re, collections, bisect
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import cfg, bl_targets, push_entries, dec
from slice import provenance

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
LO, HI = 0x6e807c, 0x6ec200

ent = sorted(set(s for s in b.fmap if LO <= s < HI) | bl_targets(LO, HI) | push_entries(LO, HI))
acq_all = b.calls_to(ACQ)
acq_tu = [s for s in acq_all if LO <= s < HI]

def unit_of(site):
    idx = bisect.bisect_right(ent, site) - 1
    for j in range(idx, -1, -1):
        e = ent[j]
        lim = ent[j + 1] if j + 1 < len(ent) else HI
        ins, _, _, _ = cfg(e, lim)
        if site in ins:
            return e, lim
    return None, None

units = sorted(set(unit_of(s)[0] for s in acq_tu if unit_of(s)[0]))
print('units', len(units))
# callers of each unit
callers = {}
for u in units:
    cs = b.calls_to(u)
    if cs:
        callers[u] = cs
print('units with direct callers:', len(callers), 'total caller sites:', sum(len(v) for v in callers.values()))
# which callers also acquire something?
acq_by_unit = collections.defaultdict(list)
for s in acq_all:
    f = b.func_at(s)
    acq_by_unit[f[0]].append(s)
print()
print('=== caller functions that ALSO call acquire (possible same-object nesting) ===')
for u, cs in sorted(callers.items()):
    for c in cs:
        f = b.func_at(c)
        if f[0] in acq_by_unit:
            print('method %08x <- caller %08x (unit %08x)  caller acquires: %s' % (
                u, c, f[0], ','.join('%x' % x for x in acq_by_unit[f[0]])))
