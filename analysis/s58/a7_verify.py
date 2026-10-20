"""S58-A.4: valida build_rows (modelo) contra el código real 0x4383c9dc en Unicorn."""
import random, sys
from wtrace import W
from timing_model import build_rows
AMB = [(0x4383c9dc, 0x4383cc40), (0x4383c7e0, 0x4383c818), (0x43550000, 0x43570000), (0x43b08000, 0x43b0b000), (0x43ad0000, 0x43ae0000)]
GB, G224 = 0x45400000, 0x45500000
def real(w, G):
    w.u.mem_write(GB, bytes(0x400)); w.u.mem_write(G224, bytes(0x100))
    for i in range(4): w.w32(GB + 0xb0 + 4 * i, G['b0'][i]); w.w32(GB + 0xc0 + 4 * i, G['c0'][i]); w.w32(GB + 0xd0 + 4 * i, G['d0'][i])
    for k in ('10', '14', '18', '28', '2a', '2c', '2e', '38'): w.w16(GB + int(k, 16), G[k])
    for k in ('16', '24', '3a', '163', '164', '190'): w.u.mem_write(GB + int(k, 16), bytes([G[k]]))
    w.w32(GB + 0x30, G['30']); w.w32(GB + 0x34, G['34'])
    w.call(0x4383c9dc, GB, G224)
    out = []
    for i in range(4):
        b = G224 + 0x2c + 16 * i
        out.append(dict(shd=w.r16(b), shd_hi=w.r16(b + 2), svd=w.r16(b + 4), spl=w.r16(b + 6), f36=w.r16(b + 10), f38=w.r16(b + 12), f3a=w.r16(b + 14)))
    return out
def rnd_G(r):
    return dict(b0=[r.choice([0, 100, r.randrange(1 << 16), r.randrange(1 << 32)]) for _ in range(4)], c0=[r.randrange(1 << 13) for _ in range(4)], d0=[r.choice([0, 1, 2, 5, r.randrange(1 << 8)]) for _ in range(4)],
                **{'10': r.choice([4176, r.randrange(1 << 16)]), '14': r.randrange(0, 50), '18': r.randrange(0, 200), '28': r.randrange(1 << 12), '2a': r.randrange(1 << 8), '2c': r.choice([0, 864, r.randrange(1 << 12)]),
                   '2e': r.randrange(1 << 12), '38': r.choice([0, 1, 2, 3, r.randrange(1, 100)]), '16': r.choice([0, 1, 2, 3, 4, r.randrange(256)]), '24': r.choice([0, 1]), '3a': r.choice([0, 1]),
                   '163': r.choice([0, 1]), '164': r.choice([0, 1]), '190': r.choice([0, 1]), '30': r.choice([1, 2, 3, 6, r.randrange(1, 40)]), '34': r.choice([0, 0, 0, 1, 2])})
def main(n=300):
    r = random.Random(581); ok = tot = 0; bad = []
    for k in range(n):
        G = rnd_G(r)
        for fill in (0, 0xa5):
            w = W(ambito=AMB, fill=fill); got = real(w, G); exp = build_rows(G)
            tot += 1; good = got == exp; ok += good
            if not good and len(bad) < 3: bad.append((G, got, exp))
    print('build_rows modelo == código real:', ok, '/', tot)
    for b in bad: print(b)
if __name__ == '__main__': main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
