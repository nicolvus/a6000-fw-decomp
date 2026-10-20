"""S58-C.1: CORRECCIÓN de la matriz IMX235 de S57. SetMode A7S (virtual +0xa0 = 0x436f3928): col = maptab[idx_modo] (34 bytes @0x43c9c5b5); cada fila = {u32 ptr_dato, 16 bytes (una por columna)}, paso 0x14 (no 40 B x 34 modos).
Registro = 6 B {u16 dev, u16 dirección, u16 dato} en 0x44021ebc (98)."""
import struct
from tdis import data, B, u32
d = data('A7S')
MT, MAP, RT, NM = 0x43fee370, 0x43c9c5b5, 0x43fee598, 34
modes = [u32('A7S', MT + 4 * i) for i in range(NM)]
mapcol = list(d[MAP - B:MAP - B + NM])
def rows():
    out, a = [], RT
    while True:
        p = u32('A7S', a)
        if not (B < p < B + len(d)): break
        rec = d[p - 4 - B:p + 2 - B]
        if rec[0] not in (0x81, 0x83): break
        out.append(dict(row=a, ptr=p, dev=rec[0], addr=struct.unpack('<H', rec[2:4])[0], init=rec[4], cols=list(d[a - B + 4:a - B + 0x14]))); a += 0x14
    return out
R = rows()
def value(row, mode): return row['cols'][mapcol[modes.index(mode)]]
if __name__ == '__main__':
    print('modos', [hex(m) for m in modes]); print('maptab', mapcol); print('filas', len(R), 'columnas usadas', sorted(set(mapcol)))
    for m in (0x0b, 0x4c, 0x4d, 0x4e, 0x4f, 0x35): print(hex(m), 'idx', modes.index(m), 'col', mapcol[modes.index(m)])
    # comparar columnas Silent vs vecinos
    def cmp(a, b): return [(hex(r['addr']), hex(value(r, a)), hex(value(r, b))) for r in R if value(r, a) != value(r, b)]
    for a, b in ((0x4c, 0x4e), (0x4d, 0x4f), (0x4e, 0x4f), (0x4c, 0x4d), (0x0b, 0x4e), (0x0b, 0x4c), (0x0b, 0x35)):
        c = cmp(a, b); print(hex(a), 'vs', hex(b), len(c), c[:14])
