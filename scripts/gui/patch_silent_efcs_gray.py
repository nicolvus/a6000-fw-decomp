#!/usr/bin/env python3
"""G22-A — Parche de GUI: gris de EFCS con Silent On.

Modifica libObj.so para que, cuando Silent Shooting está ON, el menú EFCS
se ponga en gris (inhibido) y no se pueda cambiar; y cuando Silent está OFF,
EFCS vuelva a ser editable.

Mecanismo localizado en libObj.so VA 0x988e0c (manejador LIRO 0x40e3 de Silent):
  - 0x988d80: ldr.w r0, [r4, #0x164]   ; r0 = FactorId del nodo (debería ser 0x4B = EFCS)
  - 0x988d84: movw r1, #0x86f          ; r1 = valor de inhibición
  - 0x988d88: movs r2, #1              ; r2 = enable = SIEMPRE 1 (activar)
  - 0x988d8a: blx  #0xde7a8            ; ChangeInhFactorStatus(r0, r1, r2)

Cambio: 0x988d88: movs r2, #1  →  mov r2, r6
Donde r6 = resultado de 0xe0c68(ID=0x9551), asumido como el estado de Silent
(0 = Off, 1 = On). Así:
  - Silent On  → r2 = 1 → EFCS se pone en gris (inhibido)
  • Silent Off → r2 = 0 → EFCS se desinhibe (editable)

ADVERTENCIA (10-11-2026): NO USAR sin verificar. (1) La codificacion original 0x4560 era `cmp r0, ip`; la correcta de `mov r2, r6` es 0x4632.
(2) El bloque 0x988cc2..0x988f72 se activa con id 0x404 (0xde360()==0x404), no con LIRO 0x40e3; r6 = 0xe0c68(0x9551)
(tras 0xdc92c si != 0) no esta demostrado que sea 0/1 de Silent. Sin prueba en emulador ni camara.

Uso:
    python3 patch_silent_efcs_gray.py libObj.so libObj.so.patched
"""

import struct
import sys


def patch_libobj(data: bytes) -> bytes:
    """Cambia `movs r2, #1` (0x2201) por `mov r2, r6` (0x4632) en 0x988d88."""
    offset = 0x988d88

    w = struct.unpack_from('<H', data, offset)[0]
    if w != 0x2201:
        raise ValueError(
            f"En 0x{offset:08x} se esperaba 0x2201 (movs r2, #1), "
            f"se encontró 0x{w:04x}. ¿Binario diferente?"
        )

    data = data[:offset] + struct.pack('<H', 0x4632) + data[offset + 2:]
    print(f"Parche aplicado en 0x{offset:08x}: movs r2,#1 → mov r2,r6")
    return data


def main():
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} libObj.so libObj.so.patched")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]

    with open(src, 'rb') as f:
        data = f.read()

    patched = patch_libobj(data)

    with open(dst, 'wb') as f:
        f.write(patched)

    print(f"Escrito: {dst}")


if __name__ == '__main__':
    main()
