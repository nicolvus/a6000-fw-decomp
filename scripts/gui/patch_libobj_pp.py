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


# --- Gamma: ITU709(800%) y S-Log2 (G25) -------------------------------------------------------------------------------------------------
# La A7S acepta 12 valores de app en el caso 7 de `pvt_ChangePictureProfileParamApp2Obj`: 10 → VALUEID 0x481 (ITU709(800%)), 11 → 0x480 (S-Log2) (A7S libObj 0x3d2120 y su inversa
# 0x3d1888), con la conversión UI→app de `…PictureProfileGamma::convertValueIdToBackupValue` (UI 7 → 10, 8 → 11). La A6000 ya conoce los VALUEID y los convierte a selector
# 10/11 en `CamMsgConv`. Aquí se reescribe el caso 7 (80 B) con una tabla de 12 halfwords y se añade la inversa (`Obj2App`) en un trampolín.
APP2OBJ, OBJ2APP_SITE, STUB = 0x4B4774, 0x4B4390, 0x4B479C
VALUEID = (0x1B7, 0x1B8, 0x1B9, 0x1BA, 0x39C, 0x39D, 0x39E, 0x39F, 0x3A0, 0x3A1, 0x481, 0x480)
ORIG_CASE7 = bytes.fromhex("092d" "00f28e80")                   # cmp r5,#9; bhi.w error (little endian)
ORIG_SITE = bytes.fromhex("63d1" "07e0")                        # bne 0x4b445a; b 0x4b43a4


def _hw(*w):
    return b"".join(x.to_bytes(2, "little") for x in w)


def b_w(at, to):
    o = to - (at + 4)
    s, i1, i2 = (o >> 24) & 1, (o >> 23) & 1, (o >> 22) & 1
    j1, j2 = (~(i1 ^ s)) & 1, (~(i2 ^ s)) & 1
    return _hw(0xF000 | (s << 10) | ((o >> 12) & 0x3FF), 0x9000 | (j1 << 13) | (j2 << 11) | ((o >> 1) & 0x7FF))


def bcc_w(at, to, cond):                                        # T3, ±1 MiB
    o = to - (at + 4)
    return _hw(0xF000 | ((o >> 20) & 1) << 10 | cond << 6 | ((o >> 12) & 0x3F), 0x8000 | ((o >> 19) & 1) << 13 | ((o >> 18) & 1) << 11 | ((o >> 1) & 0x7FF))


def movw(rd, v):
    return _hw(0xF240 | ((v >> 11) & 1) << 10 | (v >> 12), ((v >> 8) & 7) << 12 | rd << 8 | (v & 0xFF))


def patch_gamma(d: bytes) -> bytes:
    segs = A._segments(d)
    o7, os_, ost = (A._off(segs, x) for x in (APP2OBJ, OBJ2APP_SITE, STUB))
    assert d[o7:o7 + 6] == ORIG_CASE7 and d[os_:os_ + 4] == ORIG_SITE, "libObj.so no es el fw3.21 esperado"
    out = bytearray(d)
    code = _hw(0x2D0B) + d[o7 + 2:o7 + 6]                        # cmp r5,#11; bhi.w (misma instrucción)
    code += _hw(0xA302) + _hw(0xF833, 0x3015) + _hw(0xE000 | ((0x4B4852 - (APP2OBJ + 0xC + 4)) >> 1)) + _hw(0xBF00)   # adr r3,tabla; ldrh.w r3,[r3,r5,lsl #1]; b 0x4b4852; nop
    code += b"".join(_hw(v) for v in VALUEID)                    # tabla en 0x4b4784
    assert len(code) == 0x4B479C - APP2OBJ
    out[o7:o7 + len(code)] = code
    at = STUB
    st = movw(3, 0x3A1) + _hw(0x42AB) + bcc_w(at + 6, 0x4B43A4, 0)            # r5 == 0x3a1 → app 9 (como antes)
    st += movw(3, 0x481) + _hw(0x42AB) + _hw(0xD000 | 6)                      # r5 == 0x481 → L10 (0x4b47bc)
    st += _hw(0x3B01) + _hw(0x42AB) + bcc_w(at + len(st) + 4, 0x4B445A, 1)    # r3 = 0x480; r5 != r3 → error (0x4b445a)
    st += _hw(0x230B) + b_w(at + len(st) + 2, 0x4B4416)                       # 0x480 → app 11
    st += _hw(0x230A) + b_w(at + len(st) + 2, 0x4B4416)                       # 0x481 → app 10
    assert len(st) <= 0x4B47C4 - STUB, len(st)
    out[ost:ost + 0x4B47C4 - STUB] = st + _hw(0xBF00) * ((0x4B47C4 - STUB - len(st)) // 2)
    out[os_:os_ + 4] = b_w(OBJ2APP_SITE, STUB)
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
