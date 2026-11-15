#!/usr/bin/env python3
"""G43 — Lista ISO hasta 51200 en el menú ISO de la A6000 (fw3.21+). Solo escribe una copia parcheada de `CautionConfig.so`; no construye CFW.

`CmnViewSettingNodeISOSensitivity::_getSubNode` (CautionConfig.so+0x107d7c) lee el id 0x1070316 (tipo de modelo) y, con `tbb`, elige una lista
estática de nodos. El caso de la A6000 (tipo 29) apunta a `…ISOSensitivityType12` (AUTO, 100…25600); `Default` llega a 51200. El parche cambia los dos
literales de pool (desplazamientos GOT) de ese caso por los de `Default`, igual que G39 con Calidad. 8 bytes.
Uso: iso_list_patch.py ENTRADA.so SALIDA.so   (valida los bytes originales; idempotente sobre el resultado)
"""
import struct
import sys

LIT = (0x107E80, 0x107E84)                 # literales del caso tipo 29 (tbb en 0x107da4): GOT→nodos Type12, GOT→NumOf Type12
OLD = (0x171C, 0x2AC0)                      # Type12
NEW = (0x16F8, 0x9578)                      # Default (literales en 0x107e88/0x107e8c)


def patch(d: bytes) -> bytes:
    u32 = lambda a: struct.unpack_from("<I", d, a)[0]
    assert (u32(0x107E88), u32(0x107E8C)) == NEW, "literales de Default distintos del fw3.21"
    cur = (u32(LIT[0]), u32(LIT[1]))
    if cur == NEW:
        return d
    assert cur == OLD, f"literales inesperados {cur}"
    out = bytearray(d)
    struct.pack_into("<II", out, LIT[0], *NEW)
    return bytes(out)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    open(dst, "wb").write(patch(open(src, "rb").read()))
    print("ok", dst)
