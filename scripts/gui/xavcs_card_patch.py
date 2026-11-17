#!/usr/bin/env python3
"""G79 — quita la restricción de tarjeta de XAVC S (A6000 fw3.21). Solo escribe una copia parcheada de `libObj.so`.

`ObjMedia` (libObj, tras montar la tarjeta, 0x942156): si el sistema de ficheros no es exFAT (`[+0x2c8] != 4`) o, con exFAT, la clase no es SDXC
(`[+0x2a2]` ∉ {0x8402, 0x8004, 0x8005}), pone el factor `0x20000` de su estado de inhibición (0x94a8a4). Con él, MOVIE en XAVC S muestra «Esta tarjeta de
memoria no admite la grabación de películas XAVC S» (texto 0xf633). MP4/AVCHD no se ven afectados (con la misma tarjeta FAT32 graban de fábrica).
El parche cambia `mov r0, r4` (0x94217e, destino del «no exFAT» y del «clase no SDXC») por `b.n 0x942202`, la salida normal: nunca se pone el factor.
Límite: con FAT32 un fichero no puede pasar de 4 GB (XAVC S 50 Mbps ≈ 11 min); `libmpr` tiene división automática de XAVC S
(`AutoDivideXavcContentCmd`), NO_VERIFICADO que se active por tamaño de fichero.
Uso: xavcs_card_patch.py ENTRADA.so SALIDA.so   (valida los bytes originales; idempotente sobre el resultado)
"""
import sys
from pathlib import Path

SITIO = 0x94217E
ORIG = bytes.fromhex("20464ff40031")    # mov r0, r4 ; mov.w r1, #0x20000
NUEVO = bytes.fromhex("40e04ff40031")   # b.n 0x942202 ; (resto intacto, ya no se ejecuta)
ANCLA = (0x942176, bytes.fromhex("48f20243"))   # movw r3, #0x8402 (la comparación de clase SDXC)


def patch(d: bytes) -> bytes:
    a, ancla = ANCLA
    assert d[a:a + 4] == ancla, "ancla distinta del libObj 3.21"
    cur = d[SITIO:SITIO + len(ORIG)]
    if cur == NUEVO:
        return d
    assert cur == ORIG, f"bytes inesperados {cur.hex()}"
    return d[:SITIO] + NUEVO + d[SITIO + len(NUEVO):]


if __name__ == "__main__":
    src, dst = map(Path, sys.argv[1:3])
    dst.write_bytes(patch(src.read_bytes()))
    print("ok", dst)
