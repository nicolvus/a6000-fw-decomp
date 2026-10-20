"""S58-A.2: quién escribe en G=0x43eb05d8 (+0..+0x224) durante 0x437b5e70 (AE: 0x4383d18c, 0x4383d704, 0x4383bc6c...)."""
import sys, collections, random
from wtrace import W
G = 0x43eb05d8; T = 0x45200000
AMB = [(0x43830000, 0x438f0000), (0x43ae0000, 0x43af0000), (0x43b00000, 0x43b10000), (0x437b0000, 0x437b7000)]
res = collections.defaultdict(set)
for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 12):
    w = W(ambito=AMB, fill='rand', seed=seed, ranges=[(G, G + 0x330, 'G')])
    r = random.Random(77 + seed)
    for off in range(0, 0x330, 2): w.w16(G + off, r.randrange(0x10000) if r.random() < .4 else r.choice([0, 1, 2, 0x1000]))
    obj = 0x45300000; w.w32(obj + 8, T)
    w.call(0x437b5e70, obj)
    for pc, a, sz, v, tag in w.writes: res[(a - G, sz)].add(hex(pc))
for k in sorted(res): print(hex(k[0]), k[1], sorted(res[k])[:6])
