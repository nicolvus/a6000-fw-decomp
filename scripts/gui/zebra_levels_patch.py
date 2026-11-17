#!/usr/bin/env python3
"""G83/G84 — Niveles de Zebra de `libObj.so` (A6000 fw3.21). Escribe una copia con otros centros de banda; no construye CFW.

`ObjRenderer` (libObj+0x2b9944…) traduce el índice de menú Zebra 0–7 (`tbb` en 0x2b994c) a un centro en % (`movs r3,#imm`): 70, 75, 80, 85, 90, 95, 100, 104;
la banda enviada al VDF es L = centro−5, U = centro+5 (bytes +0xb/+0xc de la petición `SetZebra`). Cada centro es 1 byte inmediato.
Uso: zebra_levels_patch.py ENTRADA.so SALIDA.so [c0 c1 … c7]   (centros 5–104 en %; por defecto 10 para el índice 0, el resto de fábrica)
"""
import sys
from pathlib import Path

SITIOS = [0x2B999E, 0x2B99A2, 0x2B9954, 0x2B9958, 0x2B995C, 0x2B9960, 0x2B9964, 0x2B9968]  # offset del imm8 de cada `movs r3,#c` (índice de menú 0–7)
FABRICA = [70, 75, 80, 85, 90, 95, 100, 104]


def patch(d: bytes, centros: list[int]) -> bytes:
    assert len(centros) == 8 and all(5 <= c <= 104 for c in centros), "8 centros entre 5 y 104 %"
    out = bytearray(d)
    for a, c in zip(SITIOS, centros):
        assert out[a + 1] == 0x23, f"{a:#x}: no es `movs r3,#imm` (fw3.21 esperado)"
        out[a] = c
    return bytes(out)


if __name__ == "__main__":
    src, dst, *c = sys.argv[1:]
    cen = [int(x) for x in c] or [10] + FABRICA[1:]
    d = Path(src).read_bytes()
    assert [d[a] for a in SITIOS] in (FABRICA, cen), "tabla de niveles distinta de fábrica"
    Path(dst).write_bytes(patch(d, cen))
    print("ok", dst, cen)
