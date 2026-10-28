"""Busca por patrón de bytes accesos Thumb-2 [Rn,#imm12] (str/ldr .w/.h/.b) a un desplazamiento dado.
Uso: scan_field.py 0xOFF [lo hi]. Imprime dirección, tipo (R/W), ancho y registro base. Linealmente robusto
(no depende de sincronizar el desensamblado con pools de literales)."""
import struct
import sys

from fw import BASE, _data

off = int(sys.argv[1], 16)
lo = int(sys.argv[2], 16) if len(sys.argv) > 2 else BASE
hi = int(sys.argv[3], 16) if len(sys.argv) > 3 else BASE + len(_data)
KIND = {0xF8C0: ("W", "32"), 0xF8D0: ("R", "32"), 0xF8A0: ("W", "16"), 0xF8B0: ("R", "16"),
        0xF880: ("W", "8"), 0xF890: ("R", "8")}
for a in range(lo, hi - 3, 2):
    h1, h2 = struct.unpack("<HH", _data[a - BASE:a - BASE + 4])
    k = KIND.get(h1 & 0xFFF0)
    if k and (h2 & 0xFFF) == off:
        print(f"{a:08x} {k[0]}{k[1]} base=r{h1 & 15} rt=r{h2 >> 12}")
