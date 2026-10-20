"""S58-A.5: ¿quién llena el bloque de temporización de modo P+0x4c4..0x4f8 (M: línea/frame/VMAX/svr/HMAX)? memcpy con registro + almacenes durante 0x437b5b14."""
import sys, collections, random
from wtrace import W
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_LR
P = 0x43eaee84
AMB = [(0x43830000, 0x438f0000), (0x43ae0000, 0x43af0000), (0x43b00000, 0x43b10000), (0x437b0000, 0x437b7000), (0x43550000, 0x43570000), (0x43ad0000,0x43ae0000)]
log: list[tuple] = []
def memcpy(w):
    u = w.u; d, s_, n = u.reg_read(UC_ARM_REG_R0), u.reg_read(UC_ARM_REG_R1), u.reg_read(UC_ARM_REG_R2)
    if P + 0x4c0 <= d < P + 0x500 or (d <= P + 0x4c0 < d + n): log.append(('memcpy', hex(u.reg_read(UC_ARM_REG_LR)), hex(d - P), n, hex(s_)))
    try: u.mem_write(d, bytes(u.mem_read(s_, n)))
    except Exception: pass
    return d
res = collections.defaultdict(set)
for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6):
    w = W(ambito=AMB, fill='rand', seed=seed, ranges=[(P + 0x4c0, P + 0x500, 'M')], stubfn={0x439c5320: memcpy, 0x4355faf0: None} if False else {0x439c5320: memcpy})
    r = random.Random(11 + seed)
    for off in range(0, 0x900, 2): w.w16(P + off, r.randrange(0x10000) if r.random() < .3 else r.choice([0, 1, 2, 3, 4, 0x1000]))
    obj = 0x45300000; w.w32(obj + 8, 0x45200000); w.w32(obj + 0x20, 0x45240000); w.w32(obj + 4, 0x45280000)
    w.call(0x437b5b14, obj, 0x45310000, count=8000000)
    for pc, a, sz, v, tag in w.writes: res[(a - P, sz)].add(hex(pc))
for k in sorted(res): print('store', hex(k[0]), k[1], sorted(res[k])[:4])
for l in sorted(set(log)): print(l)
