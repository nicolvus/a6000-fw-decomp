"""S58-A.3: ¿quién escribe el estado AE P=0x43eaee84 (+0x4c4..0x500, +0x22c, +0x248) y AEOUT3=0x43eada70 (+0x348..0x378)? ejecuta 0x437b5b14 (pipeline AE)."""
import sys, collections, random
from wtrace import W
P = 0x43eaee84; A3 = 0x43eada70
AMB = [(0x43830000, 0x438f0000), (0x43ae0000, 0x43af0000), (0x43b00000, 0x43b10000), (0x437b0000, 0x437b7000), (0x43720000,0x43730000), (0x436e0000,0x436f1000)]
res = collections.defaultdict(set)
nstub: collections.Counter[int] = collections.Counter()
for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6):
    w = W(ambito=AMB, fill='rand', seed=seed, ranges=[(P, P + 0x800, 'P'), (A3, A3 + 0x400, 'A3')])
    r = random.Random(7 + seed)
    for base in (P, A3):
        for off in range(0, 0x800, 2): w.w16(base + off, r.randrange(0x10000) if r.random() < .4 else r.choice([0, 1, 2, 0x1000]))
    obj = 0x45300000; w.w32(obj + 8, 0x45200000)
    w.call(0x437b5b14, obj, 0x45310000, count=6000000)
    for pc, a, sz, v, tag in w.writes: res[(tag, a - (P if tag == 'P' else A3), sz)].add(hex(pc))
    nstub.update(w.stubbed)
for k in sorted(res): print(k[0], hex(k[1]), k[2], sorted(res[k])[:4])
print('stubbed top', [(hex(a), n) for a, n in nstub.most_common(25)])
