"""S57-C: transformación (svd,shd,spl,ShutMode) -> registros sombra 3..8, 0x144..0x149, 0x100/0x101 con el SetExposure real.
Arg (r1 de 0x436d6f6c): +0 u16 = shd, +4 u16 = svd, +6 u16 = spl, +9 u8 = ShutMode (log 'SetExps' de 0x436d723a: svd=r6(+4), shd=r5(+0), spl=r7(+6)).
Valida con dos rellenos de memoria (0x00 / 0xA5) y vectores aleatorios con semilla fija."""
import sys, struct, random
sys.path.insert(0, '.')
from emu57 import B, Emu, R, set_exposure
ID = {i: p for p in R.recs for i in [R.recs[p]]}   # id -> último registro (ID1 duplicado: no se usa aquí)
def regs(e, ids): return {i: e.reg(next(p for p in R.recs if R.recs[p] == i)) for i in ids}
IDS = [3, 4, 5, 6, 7, 8, 0x100, 0x101, 0x144, 0x145, 0x146, 0x147, 0x148, 0x149]
def run(shd, svd, spl, shut, fill=0, mirror_flag=None, w10=0, w12=0, b8=0, b14=0):
    e = Emu(fill=fill); e.new_obj(); e.setf(0x170, 0xb, 4); e.setf(0x174, 0xb, 4)
    if mirror_flag is not None: e.u.mem_write(struct.unpack_from('<I', R.d, 0x4401eee4 + 0x4f24 - B)[0] + 0x7f, bytes([mirror_flag]))
    before = regs(e, IDS)
    set_exposure(e, shut, w0=shd, w4=svd, w6=spl, w10=w10, w12=w12, b8=b8, b14=b14)
    return before, regs(e, IDS), e
def model(shd, svd, spl):
    return {3: svd & 0xff, 4: (svd >> 8) & 0xf, 5: shd & 0xff, 6: (shd >> 8) & 0x3f, 7: spl & 0xff, 8: (spl >> 8) & 0xf}
if __name__ == '__main__':
    rnd = random.Random(57); res = []
    for k in range(200):
        shd, svd, spl = rnd.randrange(0x10000), rnd.randrange(0x10000), rnd.randrange(0x10000); shut = rnd.randrange(5)
        for fill in (0x00, 0xa5):
            b, a, e = run(shd, svd, spl, shut, fill, mirror_flag=0xff)
            m = model(shd, svd, spl)
            # reg4/6/8 solo cambian los bits bajos (bfi): comparar bits bajos y comprobar preservación de los altos
            ok = all((a[i] & msk) == (m[i] & msk) for i, msk in ((3, 255), (4, 15), (5, 255), (6, 63), (7, 255), (8, 15)))
            keep = all((a[i] & ~msk & 255) == (b[i] & ~msk & 255) for i, msk in ((4, 15), (6, 63), (8, 15)))
            res.append((ok, keep, fill))
    print('modelo bits bajos OK', sum(r[0] for r in res), '/', len(res), '| preserva bits altos', sum(r[1] for r in res), '/', len(res))
    # espejo 0x144..0x149 y ShutMode 2 (0x100/0x101)
    b, a, e = run(0x1234, 0xabc, 0x567, 1, 0, mirror_flag=0x00); print('espejo (flag!=0xff):', {hex(i): hex(v) for i, v in a.items() if i >= 0x144})
    b, a, e = run(0x1234, 0xabc, 0x567, 1, 0, mirror_flag=0xff); print('espejo (flag==0xff):', {hex(i): hex(v) for i, v in a.items() if i >= 0x144})
    for shut in (1, 2):
        b, a, e = run(0x1234, 0xabc, 0x567, shut, 0, w10=0x5aa5, w12=0x33cc, b8=7, b14=9); print('shut', shut, '0x100/0x101:', hex(a[0x100]), hex(a[0x101]), 'mem 0xA5:', end=' ')
        b, a, e = run(0x1234, 0xabc, 0x567, shut, 0xa5, w10=0x5aa5, w12=0x33cc, b8=7, b14=9); print(hex(a[0x100]), hex(a[0x101]))
