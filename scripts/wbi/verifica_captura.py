"""¿Se tomó esta instantánea en las mismas condiciones que la WBI de fábrica?

Uso (raíz del repo): python3 scripts/wbi/verifica_captura.py IMAGEN [IMAGEN...]
Sale con 1 si alguna condición no se cumple. Condiciones (reports/film-pb-1-wbi-escalera-ssbi-20261128.md §2 y §2b):
  1. Último apagado en upm.ko = {0x920141, 0x27, 0x1c, 0x20} (libObj Inactivate -> PowerOff, OFF_TYPE_COLDOFF).
  2. Palabra wbi_memclr (PA 0x800210e8, cmdline `wbi_memclr=`) = 1: el kernel puso a cero las regiones wbimem=.
  3. Fondo de las 12 regiones wbimem= a 0x00 (ninguna página entera a 0xFF).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upm_modulo
from snapram import Missing, Ram

MEMCLR_PA = 0x800210E8
WBIMEM = [(0x1000, 0x80021000), (0xE5000, 0x82D90000), (0x8000, 0x82EAE000), (0x500000, 0x82FC0000),
          (0x30000, 0x96800000), (0x80000, 0x8E680000), (0x384E000, 0x8F708000), (0x1E000, 0x9334F000),
          (0x2000, 0x93383000), (0x680000, 0x933AD000), (0xEC000, 0x96083000), (0x200000, 0x96600000)]
FABRICA = (0x920141, 0x27, 0x1C, 0x20)


def paginas(r, pa, n):
    for o in range(0, n, 4096):
        try:
            yield r.read(pa - 0x40000000 + o, 4096)
        except Missing:
            yield None


def comprueba(path):
    r = Ram(Path(path))
    base, pr = upm_modulo.localiza(r, upm_modulo.texto_ko())
    reg = struct.unpack('<4I', upm_modulo.lee_va(r, pr, base + upm_modulo.TEXT_A_GOFF + 4, 16))
    memclr = struct.unpack('<I', r.read(MEMCLR_PA - 0x40000000, 4))[0]
    ff = cero = total = 0
    for n, pa in WBIMEM:
        for pg in paginas(r, pa, n):
            if pg is None:
                continue
            total += 1
            ff += pg == b'\xff' * 4096
            cero += pg == bytes(4096)
    res = {'registro upm = fábrica': reg == FABRICA, 'wbi_memclr = 1': memclr == 1, 'wbimem sin páginas 0xFF': ff == 0}
    print(f'{path}:')
    print(f'  upm último apagado {", ".join(hex(x) for x in reg)}; wbi_memclr {memclr}; '
          f'wbimem {total} páginas: {cero} a cero, {ff} enteras a 0xFF')
    for k, v in res.items():
        print(f'  {"OK " if v else "NO "} {k}')
    return all(res.values())


if __name__ == '__main__':
    resultados = [comprueba(p) for p in sys.argv[1:]]  # todas, sin cortocircuito
    sys.exit(0 if all(resultados) else 1)
