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


# --- Gamma: ITU709(800%), S-Log2 y S-Log3 (G25/G26) --------------------------------------------------------------------------------------
# La A7S acepta 12 valores de app en el caso 7 de `pvt_ChangePictureProfileParamApp2Obj`: 10 → VALUEID 0x481 (ITU709(800%)), 11 → 0x480 (S-Log2) (A7S libObj 0x3d2120 y su inversa
# 0x3d1888); la A6300 añade 12 → 0x585 (S-Log3) (A6300 libObj 0x425446, `tbb` de 13 casos en 0x4253ec). Con la conversión UI→app de `…PictureProfileGamma::convertValueIdToBackupValue`
# (UI 7 → 10, 8 → 11, 9 → 12). La A6000 ya conoce los VALUEID 0x480/0x481 y los convierte a selector 10/11 en `CamMsgConv`; 0x585 → 12 se añade aquí.
# Los tres sitios pasan a ser una búsqueda en la misma tabla de 13 halfwords: índice = valor de app = selector del núcleo.
APP2OBJ, OBJ2APP_SITE, STUB = 0x4B4774, 0x4B4390, 0x4B479E
TABLA = 0x4B4784
CAMCONV, CAMCONV_FIN, CAMCONV_ERR, CAMCONV_STORE = 0x9B36DE, 0x9B3744, 0x9B3770, 0x9B3744
VALUEID = (0x1B7, 0x1B8, 0x1B9, 0x1BA, 0x39C, 0x39D, 0x39E, 0x39F, 0x3A0, 0x3A1, 0x481, 0x480, 0x585)
ORIG_CASE7 = bytes.fromhex("092d" "00f28e80")                   # cmp r5,#9; bhi.w error (little endian)
ORIG_SITE = bytes.fromhex("63d1" "07e0")                        # bne 0x4b445a; b 0x4b43a4
ORIG_CAMCONV = bytes.fromhex("40f29d33" "9842" "0646")          # movw r3,#0x39d; cmp r0,r3; mov r6,r0


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


def bcc(at, to, cond):                                          # T1, −256…+254 B
    return _hw(0xD000 | cond << 8 | (((to - (at + 4)) >> 1) & 0xFF))


def b_n(at, to):                                                # T2, ±2 KiB
    return _hw(0xE000 | (((to - (at + 4)) >> 1) & 0x7FF))


def adr(rd, at, to):                                            # T1 (hacia delante, destino alineado a 4) · T2/`sub` (hacia atrás)
    base = (at + 4) & ~3
    if to >= base:
        assert (to - base) % 4 == 0 and (to - base) < 1024
        return _hw(0xA000 | rd << 8 | (to - base) // 4)
    n = base - to
    return _hw(0xF2AF | ((n >> 11) & 1) << 10, ((n >> 8) & 7) << 12 | rd << 8 | (n & 0xFF))


def movw(rd, v):
    return _hw(0xF240 | ((v >> 11) & 1) << 10 | (v >> 12), ((v >> 8) & 7) << 12 | rd << 8 | (v & 0xFF))


LDRH_R1_R2_R3 = _hw(0xF832, 0x1013)                             # ldrh.w r1,[r2,r3,lsl #1]


def _busca(at, tabla, hallado, error, cmp_enc, err_largo, n=13):
    """r3 = índice del valor (r0 o r5 según `cmp_enc`) en la tabla de `n` halfwords; salta a `hallado` (con r3) o a `error`."""
    c = adr(2, at, tabla) + _hw(0x2300)                          # adr r2,tabla; movs r3,#0
    lazo = at + len(c)
    c += LDRH_R1_R2_R3 + _hw(cmp_enc)                            # ldrh.w r1,[r2,r3,lsl #1]; cmp r1,r0|r5
    c += bcc(at + len(c), hallado, 0) + _hw(0x3301) + _hw(0x2B00 | n)   # beq; adds r3,#1; cmp r3,#n
    c += bcc(at + len(c), lazo, 1)                               # bne lazo
    return c + (b_w if err_largo else b_n)(at + len(c), error)


def patch_gamma(d: bytes) -> bytes:
    segs = A._segments(d)
    o7, os_, ost, oc = (A._off(segs, x) for x in (APP2OBJ, OBJ2APP_SITE, STUB, CAMCONV))
    assert d[o7:o7 + 6] == ORIG_CASE7 and d[os_:os_ + 4] == ORIG_SITE, "libObj.so no es el fw3.21 esperado"
    assert d[oc:oc + 8] == ORIG_CAMCONV, "libObj.so no es el fw3.21 esperado (CamMsgConv)"
    out = bytearray(d)
    # App2Obj, caso 7: cmp r5,#12; bhi.w error; adr r3,tabla; ldrh.w r3,[r3,r5,lsl #1]; b 0x4b4852; nop; tabla de 13 halfwords (0x4b4784…0x4b479e)
    code = _hw(0x2D00 | (len(VALUEID) - 1)) + d[o7 + 2:o7 + 6]
    code += adr(3, APP2OBJ + 6, TABLA) + _hw(0xF833, 0x3015) + _hw(0xE000 | ((0x4B4852 - (APP2OBJ + 0xC + 4)) >> 1)) + _hw(0xBF00)
    code += b"".join(_hw(v) for v in VALUEID)
    assert APP2OBJ + len(code) == STUB
    out[o7:o7 + len(code)] = code
    # Obj2App: el sitio salta a una búsqueda en la misma tabla (r5 = VALUEID → r3 = valor de app → 0x4b4416); si no está, error (0x4b445a)
    fin = 0x4B47C4
    st = _busca(STUB, TABLA, STUB + 24, 0x4B445A, 0x42A9, True)      # cmp r1,r5
    st += b_w(STUB + len(st), 0x4B4416)
    assert STUB + len(st) <= fin and 24 == len(st) - 4, len(st)
    out[ost:fin] = st + _hw(0xBF00) * ((fin - STUB - len(st)) // 2)
    out[os_:os_ + 4] = b_w(OBJ2APP_SITE, STUB)
    # CamMsgConv (0x9b36de…0x9b3743): VALUEID de gamma → selector = índice en la tabla (había una cadena de comparaciones de 12 casos)
    tabla_cc = CAMCONV + 0x16
    nuevo = _hw(0x4606) + _busca(CAMCONV + 2, tabla_cc, CAMCONV_STORE, CAMCONV_ERR, 0x4281, False)   # mov r6,r0; … cmp r1,r0
    assert CAMCONV + len(nuevo) == tabla_cc and tabla_cc % 4 == 0, hex(tabla_cc)
    nuevo += b"".join(_hw(v) for v in VALUEID)
    assert CAMCONV + len(nuevo) <= CAMCONV_FIN, len(nuevo)
    out[oc:oc + CAMCONV_FIN - CAMCONV] = nuevo + _hw(0xBF00) * ((CAMCONV_FIN - CAMCONV - len(nuevo)) // 2)
    return bytes(out)


# --- Color Mode: B&W, S-Gamut, S-Gamut3 y S-Gamut3.Cine (G26) -----------------------------------------------------------------------------
# La A6300 convierte el valor de app 0–11 del Color Mode (caso 0 de `pvt_ChangePictureProfileParamApp2Obj`, `tbb` de 12 casos en 0x425378 de su libObj) en VALUEID:
# 0–4 STD/TONE1/TONE2/PRO/ITU709, 5–7 STD_MOV/STD_STL/CINEMA, 8 → 0x505 (SGAMUT), 9 → 0x504 (BW), 10 → 0x583 (SGAMUT3), 11 → 0x584 (SGAMUT3_CINE).
# La A6000 solo tiene 0–7. Igual que en Gamma, los tres sitios (App2Obj caso 0, Obj2App caso 0 y `CamMsgConv` byte 8) pasan a buscar en la misma tabla.
COLOR = (0x1AD, 0x1AE, 0x1AF, 0x1B0, 0x1B1, 0x399, 0x39A, 0x39B, 0x505, 0x504, 0x583, 0x584)
C_APP2OBJ, C_APP2OBJ_FIN = 0x4B471C, 0x4B475E
C_OBJ2APP, C_OBJ2APP_FIN = 0x4B42FA, 0x4B433A
C_CAMCONV, C_CAMCONV_FIN, C_CAMCONV_ERR, C_CAMCONV_STORE = 0x9B325E, 0x9B32C0, 0x9B32C4, 0x9B32C0
ORIG_C_APP2OBJ = bytes.fromhex("072d")                        # cmp r5,#7
ORIG_C_OBJ2APP = bytes.fromhex("b5f5d87f")                    # cmp.w r5,#0x1b0
ORIG_C_CAMCONV = bytes.fromhex("b0f5d87f")                    # cmp.w r0,#0x1b0


def patch_color(d: bytes) -> bytes:
    segs = A._segments(d)
    oa, oo, oc = (A._off(segs, x) for x in (C_APP2OBJ, C_OBJ2APP, C_CAMCONV))
    assert d[oa:oa + 2] == ORIG_C_APP2OBJ and d[oo:oo + 4] == ORIG_C_OBJ2APP and d[oc:oc + 4] == ORIG_C_CAMCONV, "libObj.so no es el fw3.21 esperado"
    out = bytearray(d)
    n = len(COLOR)
    tabla = b"".join(_hw(v) for v in COLOR)

    def pon(o, ini, fin, code):
        assert len(code) <= fin - ini, (hex(ini), len(code))
        out[o:o + fin - ini] = code + _hw(0xBF00) * ((fin - ini - len(code)) // 2)

    # App2Obj caso 0: cmp r5,#11; bhi.w error; adr r3,tabla; ldrh.w r3,[r3,r5,lsl #1]; b 0x4b4852; tabla (alineada a 4)
    code = _hw(0x2D00 | (n - 1)) + d[oa + 2:oa + 6]
    code += adr(3, C_APP2OBJ + 6, C_APP2OBJ + 16) + _hw(0xF833, 0x3015) + _hw(0xE000 | ((0x4B4852 - (C_APP2OBJ + 0xC + 4)) >> 1)) + _hw(0xBF00)
    assert len(code) == 16 and (C_APP2OBJ + 16) % 4 == 0
    pon(oa, C_APP2OBJ, C_APP2OBJ_FIN, code + tabla)
    # Obj2App caso 0: búsqueda en la tabla (r5 = VALUEID → r3 = app → 0x4b4416); si no está → 0x4b445a
    t = C_OBJ2APP + 26
    st = _busca(C_OBJ2APP, t, C_OBJ2APP + 22, 0x4B445A, 0x42A9, True, n)
    st += b_w(C_OBJ2APP + len(st), 0x4B4416)
    assert len(st) == 26 and t % 4 == 0, (len(st), hex(t))
    pon(oo, C_OBJ2APP, C_OBJ2APP_FIN, st + tabla)
    # CamMsgConv: byte 8 = índice (el original usaba r8 = 0 y sb = 5 para STD y STD_MOV; el índice es el mismo)
    t = C_CAMCONV + 22
    cc = _hw(0x4606) + _busca(C_CAMCONV + 2, t, C_CAMCONV_STORE, C_CAMCONV_ERR, 0x4281, False, n)
    assert len(cc) == 22 and t % 4 == 0
    pon(oc, C_CAMCONV, C_CAMCONV_FIN, cc + tabla)
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
