#!/usr/bin/env python3
"""G39 — Habilita «Extra fine» en el menú Calidad (A6000 fw3.21+). Solo escribe una copia parcheada de `CautionConfig.so`; no construye CFW.

`CmnViewSettingNodeStlImageQuality::_getSubNode` (CautionConfig.so+0x108b6c) lee el id 0x1070316 y, si 1<<id casa con 0x61a00002 (incluye la A6000),
elige la lista `Type01` (RAW, RAW+J, Fine, Standard: 4 nodos); si no, `Default` (5 nodos, con `StlImageQualityExtraFine`, process id 2 →
`WRAPPER_IMAGE_QUALITY` 3 = `JPG_QUALITY_EXFINE`). El parche cambia los dos literales de pool (desplazamientos GOT) de Type01 por los de Default.
Uso: quality_exfine_patch.py ENTRADA.so SALIDA.so   (valida los bytes originales; idempotente sobre el resultado)
"""
import struct
import sys

LIT_T, LIT_N = 0x108BE0, 0x108BE4          # literales del pool de _getSubNode: GOT→nodos Type01, GOT→cuenta Type01
OLD = (0x7E38, 0x9E20)                      # Type01 (nodos, NumOf)
NEW = (0x93F8, 0x84AC)                      # Default (nodos, NumOf) — mismas ranuras GOT que usa el código del Default
MASK = (0x108BD4, 0x1070316, 0x61A00002)    # sanity: ancla del sitio (id y máscara de modelos)


def patch(d: bytes) -> bytes:
    u32 = lambda a: struct.unpack_from("<I", d, a)[0]
    assert (u32(MASK[0]), u32(MASK[0] + 4)) == MASK[1:], "ancla de _getSubNode distinta del fw3.21"
    cur = (u32(LIT_T), u32(LIT_N))
    if cur == NEW:
        return d
    assert cur == OLD, f"literales inesperados {cur}"
    out = bytearray(d)
    struct.pack_into("<II", out, LIT_T, *NEW)
    return bytes(out)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    open(dst, "wb").write(patch(open(src, "rb").read()))
    print("ok", dst)
