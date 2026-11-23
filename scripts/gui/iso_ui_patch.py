#!/usr/bin/env python3
"""G104 §8.5 — Pantalla ISO hasta 51200 (fw3.21+): la vista `ViewIsoSensitivity` de `viewUnified4.so` oculta a mano las filas.

La tabla de menú de la vista (`CmnViewMenuItemStruct`, `0x1b113c`) ya trae las filas 32000 (id `0x1f`), 40000 (`0x20`) y 51200 (`0x21`) con su
texto e icono. La función `0xf0ae0` las marca todas válidas y luego oculta una lista fija del modelo con `CmnMenuTableUtil::setValid(id, false)`.
El parche cambia `movs r2,#0` → `movs r2,#1` en esas tres llamadas (3 B). `libObj`, `WrapperIso::getIso` y `processDataMgr` ya llegan a 51200
(código `0x26`): medido en el arnés, la fila se elige y la pantalla de disparo muestra «ISO 51200».
Uso: iso_ui_patch.py ENTRADA.so SALIDA.so   (valida los bytes originales; idempotente)
"""
import sys
from pathlib import Path

# (dirección del `movs r2,#0`, id de fila que va justo antes en `movs r1,#id`)
SITIOS = ((0xF0B26, 0x21), (0xF0B32, 0x20), (0xF0B3E, 0x1F))


def patch(d: bytes) -> bytes:
    out = bytearray(d)
    for a, fila in SITIOS:
        assert out[a - 2:a] == bytes((fila, 0x21)), f"movs r1,#{fila:#x} no está en {a - 2:#x}"
        assert out[a + 1] == 0x22 and out[a] in (0, 1), f"bytes inesperados en {a:#x}: {out[a:a + 2].hex()}"
        out[a] = 1
    return bytes(out)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    Path(dst).write_bytes(patch(Path(src).read_bytes()))
    print("ok", dst)
