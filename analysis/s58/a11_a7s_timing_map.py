"""S58-C: mapeo (svd, shd, spl) -> registros IMX235 con el SetExposure A7S real (0x436f4168), vectores aleatorios, 2 rellenos de memoria."""
import random, sys
sys.path.insert(0, '.')
from a7s_emu import A7S, shadow
REG = {k: None for k in range(0x00, 0x10)}
def one(mode, shut, svd, shd, spl, fill):
    e = A7S(fill=fill); e.setmode(mode); b = shadow(e); r = e.setexposure(shd=shd, svd=svd, spl=spl, shut=shut); a = shadow(e)
    return r, {k[1]: v[1] for k, v in a.items() if k[0] == 0x81}, {k[1]: v[1] for k, v in b.items() if k[0] == 0x81}
def main(n=120):
    rnd = random.Random(58); ok = tot = 0; bad = []
    for k in range(n):
        svd, shd, spl = rnd.randrange(0x10000), rnd.randrange(0x10000), rnd.randrange(0x10000); shut = rnd.choice([0, 1, 3, 4]); mode = rnd.choice([0x0b, 0x4e, 0x4f, 0x4c])
        for fill in (0x00, 0xa5):
            r, a, b = one(mode, shut, svd, shd, spl, fill)
            exp = {2: svd & 0xff, 3: (svd >> 8) & 0xf, 4: spl & 0xff, 5: (spl >> 8) & 0xf, 6: shd & 0xff, 7: (shd >> 8) & 0x3f}
            # los bits altos de 3,5,7 se preservan del valor previo
            good = r == 0 and all((a[k2] & m) == (exp[k2] & m) and (a[k2] & ~m & 0xff) == (b[k2] & ~m & 0xff) for k2, m in ((2, 255), (3, 15), (4, 255), (5, 15), (6, 255), (7, 63)))
            tot += 1; ok += good
            if not good and len(bad) < 3: bad.append((mode, shut, svd, shd, spl, {k2: hex(a[k2]) for k2 in range(2, 8)}, {k2: hex(v) for k2, v in exp.items()}, {k2: hex(b[k2]) for k2 in range(2, 8)}))
    print('A7S SetExposure real: svd->0x02/0x03[3:0], spl->0x04/0x05[3:0], shd->0x06/0x07[5:0]:', ok, '/', tot)
    for b in bad: print(b)
if __name__ == '__main__': main(int(sys.argv[1]) if len(sys.argv) > 1 else 120)
