import sys, struct, re, collections, bisect
sys.path.insert(0, '/tmp')
from ifotool import Binary
from ifocfg import cfg, bl_targets, push_entries, dec, success_entries
from slice import provenance

b = Binary()
ACQ, REL = 0x5BAD00, 0x5BACB0
LO, HI = 0x6e81bc, 0x6ec200

acq = [s for s in b.calls_to(ACQ) if LO <= s < HI]
rel = [s for s in b.calls_to(REL) if LO <= s < HI]

# 1) provenance comparison acquire vs release
print('=== acquire/release argument provenance mismatch ===')
bad = 0
for s in acq:
    u, p = provenance(s)
    for r in rel:
        if u <= r < (u + 0x300):
            ur, pr = provenance(r)
            if (pr['kind'], pr.get('base'), pr.get('off')) != (p['kind'], p.get('base'), p.get('off')):
                print('%08x acq=%s:%s vs rel %08x %s:%s' % (s, p.get('base'), p.get('off'), r, pr.get('base'), pr.get('off')))
                bad += 1
print('mismatches:', bad)

# 2) any store to [reg,#4] inside the TU (would corrupt handle->sem)
print()
print('=== stores to [rX,#4] within mp4Ifo_If TU ===')
a = LO
hits = []
while a < 0x6ec200:
    i = dec(a)
    if i is None:
        a += 2
        continue
    ops = i.op_str.replace(' ', '')
    if i.mnemonic.startswith('str') and ',#4]' in ops and 'sp' not in ops.split(',')[0]:
        hits.append((a, i.mnemonic, i.op_str))
    a += i.size
for h in hits:
    print('%08x %-6s %s' % h)
print('count', len(hits))
