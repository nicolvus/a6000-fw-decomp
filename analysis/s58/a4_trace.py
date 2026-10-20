"""S58-A.4: 0x4383d704(X, X+0x290, X+0x860, X+0x861): ¿quién escribe X+0x290+0x348..0x378 (-> G+0xb0/0xc0/0xd0, por banco)?"""
import sys, collections, random
from wtrace import W
X = 0x43ead7e0
AMB = [(0x43830000, 0x438f0000), (0x43b00000, 0x43b10000), (0x43ad0000, 0x43ae0000), (0x43550000, 0x43570000)]
def memcpy(w):
    u = w.u; from unicorn.arm_const import UC_ARM_REG_R0 as R0, UC_ARM_REG_R1 as R1, UC_ARM_REG_R2 as R2
    d, s_, n = u.reg_read(R0), u.reg_read(R1), u.reg_read(R2); u.mem_write(d, bytes(u.mem_read(s_, n))); return d
res = collections.defaultdict(set)
nst: collections.Counter[int] = collections.Counter()
for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 10):
    w = W(ambito=AMB, fill='rand', seed=seed, ranges=[(X + 0x290 + 0x300, X + 0x290 + 0x3c0, 'A3')], stubfn={0x439c5320: memcpy})
    r = random.Random(5 + seed)
    for off in range(0, 0xa00, 2): w.w16(X + off, r.randrange(0x10000) if r.random() < .4 else r.choice([0, 1, 2, 3, 4, 0x1000]))
    w.call(0x4383d704, X, X + 0x290, X + 0x860, X + 0x861, count=6000000)
    for pc, a, sz, v, tag in w.writes: res[(a - X - 0x290, sz)].add(hex(pc))
    nst.update(w.stubbed)
for k in sorted(res): print(hex(k[0]), k[1], sorted(res[k])[:5])
print('stubbed', [(hex(a), n) for a, n in nst.most_common(12)])
