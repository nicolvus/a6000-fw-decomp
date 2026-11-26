import sys, struct, re, collections, bisect
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import cfg, exits, bl_targets, dec, push_entries

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
LO, HI = 0x6e8000, 0x6ec200

ent = sorted(set(s for s in b.fmap if LO <= s < HI) | bl_targets(LO, HI) | push_entries(LO, HI))
acq = [s for s in b.calls_to(ACQ) if LO <= s < HI]
rel = [s for s in b.calls_to(REL) if LO <= s < HI]

def unit(site):
    idx = bisect.bisect_right(ent, site) - 1
    for j in range(idx, -1, -1):
        e = ent[j]
        lim = ent[j + 1] if j + 1 < len(ent) else HI
        ins, _, _, _ = cfg(e, lim)
        if site in ins:
            return e, lim
    return None, None

units = {}
for s in acq:
    u, lim = unit(s)
    if u is None:
        print('NO-UNIT', hex(s))
        continue
    units[s] = (u, lim)

acq_units = set(u for u, _ in units.values())
print('acquire sites:', len(acq), 'units:', len(acq_units))
print()
print('=== calls from inside the critical section to another acquiring method (same class, direct bl) ===')
seen = set()
for site in [x for x in acq if x in units]:
    u, lim = units[site]
    if u in seen:
        continue
    seen.add(u)
    ins, edges, kind, call = cfg(u, lim)
    rels = [r for r in rel if u <= r < lim]
    for a in sorted(ins):
        t = call.get(a)
        if t and t in acq_units and t != ACQ:
            print('%08x(unit %08x) acq=%08x bl->%08x rel=%s  %s' % (
                a, u, site, t, ','.join('%x' % x for x in rels),
                'after-acq' if a > site else 'before-acq'))
print()
print('=== calls to another acquiring method from ANYWHERE in these units (incl. outside crit sect) ===')
n = 0
for site in [x for x in acq if x in units]:
    u, lim = units[site]
    ins, edges, kind, call = cfg(u, lim)
    for a in sorted(ins):
        t = call.get(a)
        if t and t in acq_units and t != ACQ:
            n += 1
            break
print('units with intra-class calls:', n)
