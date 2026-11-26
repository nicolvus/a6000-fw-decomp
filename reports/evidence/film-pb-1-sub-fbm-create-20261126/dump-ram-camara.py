#!/usr/bin/env python3
"""Lee la tabla FBM 0xA3699C y la tabla de pares 0x9D23FC del volcado de RAM de la cámara
(analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin, base 0x80000000).

La base de libmpr no se conoce a priori: se localiza la tabla FBM buscando el patrón de las 4
entradas con handle (idx 9 = 0x30, 18 = 0x62, 23 = 0xA0, 25 = 0xB2) dentro de una lista de 30
fileType (idx 0 = 0x10) y se deduce base = VA_tabla - 0xA3699C.
"""
import struct

DUMP = "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
d = open(DUMP, "rb").read()
print("volcado %s  %d B  (0x80000000..0x%08x)" % (DUMP, len(d), 0x80000000 + len(d)))

tabla = None
for i in range(0, len(d) - 0x14 * 30, 4):
    if d[i] != 0x30:
        continue
    if struct.unpack_from("<I", d, i + 4)[0] == 0 or struct.unpack_from("<I", d, i + 8)[0] != 1:
        continue
    if (struct.unpack_from("<I", d, i - 0x14 * 9)[0] == 0x10
            and struct.unpack_from("<I", d, i + 0x14 * 9)[0] == 0x62
            and struct.unpack_from("<I", d, i + 0x14 * 14)[0] == 0xA0
            and struct.unpack_from("<I", d, i + 0x14 * 16)[0] == 0xB2):
        tabla = i - 0x14 * 9
        break
assert tabla is not None, "tabla FBM no encontrada"
va = 0x80000000 + tabla
base = va - 0xA3699C
print("tabla 0xA3699C en VA %#x  =>  base libmpr = %#x" % (va, base))
for k in range(30):
    sect, h, v, om = struct.unpack_from("<4I", d, tabla + 0x14 * k)
    print("  idx %2d sector=%#06x handle=%#010x valido=%u om=%u" % (k, sect, h, v, om))

off = base + 0x9D23FC - 0x80000000
print("tabla de pares 0x9D23FC en VA %#x:  %s" % (base + 0x9D23FC, d[off:off + 0x18 * 3].hex(" ")))
print("  (filas 12..14 y el resto de .data/.rodata del volcado): todas a cero")
print("  .rodata comprobada (p.ej. 0x7E7BEE -> %#x): %r" % (base + 0x7E7BEE,
      d[base + 0x7E7BEE - 0x80000000:base + 0x7E7BEE - 0x80000000 + 32]))
print("  .bss de control 0xA36C78 (flag FlashLib::Init) = %s"
      % d[base + 0xA36C78 - 0x80000000:base + 0xA36C78 - 0x80000000 + 4].hex(" "))
