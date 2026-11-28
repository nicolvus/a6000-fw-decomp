"""Lee la tabla de sectores FBM (libmpr+0xA3699C, 30 x 0x14) del im.elf guardado en una instantánea WBI/prof.

Uso (desde la raíz del repo): python3 scripts/wbi/fbm_tabla.py IMAGEN [IMAGEN...]
Traduce la VA de usuario con las tablas de páginas ARMv7 cortas del propio proceso (mm->pgd en mm+0x24).
Campos por entrada: +0 sector, +4 handle, +8 válido, +0xC OM (ver reports/film-pb-1-causa-fbm-20261126.md).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from snapram import Missing, Ram

TABLA, N, PASO = 0xA3699C, 30, 0x14


class Proceso:
    def __init__(self, r, comm=b'im.elf'):
        self.r = r
        _, self.mm = next(r.tasks(comm))
        self.pgd = r.u(self.mm + 0x24)
        self.vmas = list(r.maps(self.mm))

    def fisica(self, va):
        t = self.r.u(self.pgd + 4 * (va >> 20))
        if t & 3 != 1:
            return None
        s = self.r.u((t & ~1023) - 0x40000000 + 4 * ((va >> 12) & 255))
        if not s & 2:
            return None
        return (s & ~4095) - 0x40000000 + (va & 4095)  # VA del kernel de la página física

    def lee(self, va, n):
        out = b''
        while n:
            k = min(n, 4096 - (va & 4095))
            p = self.fisica(va)
            if p is None:
                raise Missing(f'página de usuario {va:#x} no presente')
            out += self.r.read(p, k)
            va, n = va + k, n - k
        return out

    def base(self, nombre):
        return min(a for a, b, f, o, n in self.vmas if n == nombre and o == 0)


def tabla(path):
    p = Proceso(Ram(Path(path)))
    base = p.base(b'libmpr.so')
    datos = p.lee(base + TABLA, N * PASO)
    filas = [struct.unpack_from('<5I', datos, i * PASO) for i in range(N)]
    return base, filas


if __name__ == '__main__':
    for img in sys.argv[1:]:
        base, filas = tabla(img)
        con = [i for i, f in enumerate(filas) if f[1]]
        print(f'== {img}: libmpr base {base:#x}, {len(con)}/30 con handle')
        for i, f in enumerate(filas):
            if any(f):
                print(f'  idx {i:2d}: sector {f[0]:#06x} handle {f[1]:#x} valido {f[2]} om {f[3]} +0x10 {f[4]:#x}')
