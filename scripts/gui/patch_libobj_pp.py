#!/usr/bin/env python3
"""G23 — parche opcional de `libObj.so` (A6000 fw3.21): Saturation de Picture Profile con el rango de la A6300/A7S (−32…+32) en vez de −8…+7.

El validador `pvt_ChangePictureProfileParamApp2Obj` (`0x4b46b8`, caso 29 = clave `0x26c`, entrada `0x4b4880`) hace `add.w r3,r5,#8; cmp r3,#0xf`. Se cambia a `#0x20`/`#0x40`.
NO VERIFICADO: que el núcleo (`av-cam`, campo del selector `0x4066`) admita |valor| > 8; por eso es opt-in (`build_pp_menu.py --saturacion-a6300`).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A

VA = 0x4B4880
ORIG, NUEVO = bytes.fromhex("05f10803" "0f2b"), bytes.fromhex("05f12003" "402b")     # add.w r3,r5,#8; cmp r3,#0xf → #0x20; #0x40


def patch(d: bytes) -> bytes:
    o = A._off(A._segments(d), VA)
    assert d[o:o + 6] == ORIG, "libObj.so no es el fw3.21 esperado"
    return d[:o] + NUEVO + d[o + 6:]


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
