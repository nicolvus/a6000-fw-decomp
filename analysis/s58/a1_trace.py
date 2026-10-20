"""S58-A.1: quién escribe G+0x224.. (salida de 0x4383b790) y el staging de bancos G+0x250.. (-> S+0x64). Ejecuta 0x4383bf2c con estado aleatorio."""
import collections
from wtrace import W
G = 0x43eb05d8; T = 0x45200000
AMB = [(0x4383b000, 0x4383d000), (0x43b08000, 0x43b0b000), (0x4382f000, 0x43830000), (0x4386b000, 0x4386c000), (0x43b0d000, 0x43b0e000)]
res = collections.defaultdict(set); ok = 0
for seed in range(40):
    w = W(ambito=AMB, fill='rand', seed=seed, ranges=[(G + 0x224, G + 0x330, 'G224')])
    import random
    r = random.Random(1000 + seed)
    for off in range(0, 0x330, 2): w.w16(G + off, r.randrange(0x10000) if r.random() < .5 else r.choice([0, 1, 2, 0x1000]))
    w.w32(T + 0x8, T + 0x100)  # [param_1+8] ya apunta a T usado como param_5/6 : se pasan directamente
    w.w32(G + 0x20, T + 0x300);
    w.call(0x4383bf2c, G, G + 0x224, G + 0x31c, G + 0x31d, stack=(T + 0x870, T + 0xc78))
    for pc, a, sz, v, tag in w.writes: res[(hex(pc), a - G - 0x224, sz)].add(v)
    ok += 1
print(ok, 'ejecuciones')
for k in sorted(res, key=lambda k: (k[1], k[0])): print(k, len(res[k]))
