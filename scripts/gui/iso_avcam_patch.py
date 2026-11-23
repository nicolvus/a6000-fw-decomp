#!/usr/bin/env python3
"""G104 — lado `av-cam` del ISO nativo hasta 409600 (código 0x2f): topes de código y tabla ISO ampliada.

Código ISO = índice de la tabla de `av-cam` (10 … 204800 = 0x00…0x2c). Se amplía a 0x2f (256000, 320000, 409600):
- `0x43b074f2/f6` (código del ajuste → Sv, `cmp #0x2c; movhs #0x2c`) y `0x437b403e` (EXIF: `movs r1,#0x2c` antes de leer la tabla): `0x2c` → `0x2f`;
- tabla de EXIF `0x43bc48e0` (45 entradas, seguida de otros datos): copia de 48 entradas en `ZONA_B[0]` (3432 B libres en el av-cam del CFW Film) y literal
  `0x437b4124` repuntado (único acceso a la tabla, barrido de literales PC-relativos del av-cam). El original no se toca.
Aritmética: con 0x100/EV y 1/3 EV por código, 0x2f da Sv = 0x400 (sin desbordamiento). Tope de ganancia digital `0x1800` (0x4383c7a8): NO_VERIFICADO si basta (G104 §3).
Uso: iso_avcam_patch.py ENTRADA SALIDA (av-cam.bin) · apply_bytes(data) es idempotente y valida los bytes originales.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui")]
import avcam_dinamico as D

BASE = D.BASE
TOPES = ((0x43B074F2, "2c28", "2f28"), (0x43B074F6, "2c20", "2f20"), (0x437B403E, "2c21", "2f21"))
TABLA_VIEJA, LITERAL, PC_ADD = 0x43BC48E0, 0x437B4124, 0x437B404A   # PC del `add r3, pc` (0x437b4046) + 4
TABLA_NUEVA = D.ZONA_B[0]
EXTRA = (256000, 320000, 409600)
N_VIEJAS = 45


def tabla(data: bytes) -> bytes:
    return data[TABLA_VIEJA - BASE:TABLA_VIEJA - BASE + 4 * N_VIEJAS] + struct.pack("<3I", *EXTRA)


def apply_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for va, old, new in TOPES:
        cur = bytes(out[va - BASE:va - BASE + 2])
        assert cur in (bytes.fromhex(old), bytes.fromhex(new)), f"{va:#x}: {cur.hex()}"
        out[va - BASE:va - BASE + 2] = bytes.fromhex(new)
    lit = struct.unpack_from("<I", out, LITERAL - BASE)[0]
    assert lit + PC_ADD in (TABLA_VIEJA, TABLA_NUEVA), hex(lit + PC_ADD)
    tab = tabla(bytes(data))
    if lit + PC_ADD == TABLA_VIEJA:
        D.comprobar_zonas([(TABLA_NUEVA, TABLA_NUEVA + len(tab))])
        assert not any(out[TABLA_NUEVA - BASE:TABLA_NUEVA - BASE + len(tab)]), "la zona de la tabla no está a cero"
        out[TABLA_NUEVA - BASE:TABLA_NUEVA - BASE + len(tab)] = tab
        struct.pack_into("<I", out, LITERAL - BASE, (TABLA_NUEVA - PC_ADD) & 0xFFFFFFFF)
    else:
        assert bytes(out[TABLA_NUEVA - BASE:TABLA_NUEVA - BASE + len(tab)]) == tab
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(apply_bytes(Path(sys.argv[1]).read_bytes()))
    print("ok", sys.argv[2])
