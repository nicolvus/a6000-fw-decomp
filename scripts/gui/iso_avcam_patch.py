#!/usr/bin/env python3
"""G104 — lado `av-cam` del ISO nativo hasta 409600 (código 0x2f): topes de código y tabla ISO ampliada.

Código ISO = índice de la tabla de `av-cam` (10 … 204800 = 0x00…0x2c). Se amplía a 0x2f (256000, 320000, 409600):
- `0x43b074f2` (código del ajuste → Sv, `cmp #0x2c; movhs #0x2c`): `bl` a una cueva al final de `ZONA_A` que traduce los códigos de modelo
  `0x4b…0x50` (128000…409600, los de la A7S y de `iso_libobj_patch`) a `0x2a…0x2f` y topa en `0x2f`; `0x437b403e` (EXIF: `movs r1,#0x2c` antes
  de leer la tabla): `0x2c` → `0x2f`;
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
TOPES = ((0x437B403E, "2c21", "2f21"),)
# código del ajuste → Sv: `cmp r0,#0x2c; it hs; movhs r0,#0x2c` → `bl CUEVA; nop`. La cueva traduce los códigos de modelo de 128000…409600
# (`0x4b…0x50`, como la A7S; `iso_libobj_patch`) a los índices de la tabla (`0x2a…0x2f`) y aplica el tope `0x2f` (G104 §8.7).
SV, SV_ORIG, SV_G104 = 0x43B074F2, "2c2828bf2c20", "2f2828bf2f20"
CUEVA = D.ZONA_A[1] - 0x20                                           # el CFW Film ocupa ZONA_A hasta +0x29c
CUEVA_ASM = "sub.w r1, r0, #0x4b; cmp r1, #5; it ls; subls r0, #0x21; cmp r0, #0x2f; it hs; movhs r0, #0x2f; bx lr"
TABLA_VIEJA, LITERAL, PC_ADD = 0x43BC48E0, 0x437B4124, 0x437B404A   # PC del `add r3, pc` (0x437b4046) + 4
TABLA_NUEVA = D.ZONA_B[0]
EXTRA = (256000, 320000, 409600)
N_VIEJAS = 45


def tabla(data: bytes) -> bytes:
    return data[TABLA_VIEJA - BASE:TABLA_VIEJA - BASE + 4 * N_VIEJAS] + struct.pack("<3I", *EXTRA)


def _asm(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def apply_bytes(data: bytes) -> bytes:
    out = bytearray(data)
    for va, old, new in TOPES:
        cur = bytes(out[va - BASE:va - BASE + 2])
        assert cur in (bytes.fromhex(old), bytes.fromhex(new)), f"{va:#x}: {cur.hex()}"
        out[va - BASE:va - BASE + 2] = bytes.fromhex(new)
    sv, cueva = _asm(f"bl {CUEVA:#x}", SV) + bytes.fromhex("00bf"), _asm(CUEVA_ASM, CUEVA)
    cur = bytes(out[SV - BASE:SV - BASE + 6])
    if cur != sv:
        assert cur in (bytes.fromhex(SV_ORIG), bytes.fromhex(SV_G104)), f"{SV:#x}: {cur.hex()}"
        D.comprobar_zonas([(CUEVA, CUEVA + len(cueva))])
        assert not any(out[CUEVA - BASE:CUEVA - BASE + len(cueva)]), "la cueva de ZONA_A no está a cero"
        out[SV - BASE:SV - BASE + 6] = sv
        out[CUEVA - BASE:CUEVA - BASE + len(cueva)] = cueva
    assert bytes(out[CUEVA - BASE:CUEVA - BASE + len(cueva)]) == cueva
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
