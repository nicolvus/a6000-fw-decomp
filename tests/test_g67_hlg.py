"""G67: HLG1–3 — tablas (monotonía, extremos, formato), parche de curvas del núcleo y libObj (Unicorn sobre bytes reales)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
import itertools

import patch_libobj_pp as P
import pp_curves_patch as C
import pp_hlg_curves as H

AVCAM = C.ROOT / "analysis/rea-independent/input/av-cam.bin"
needs_av = pytest.mark.skipif(not (AVCAM.is_file() and C.A6300.is_file()), reason="av-cam ausente")


@pytest.mark.parametrize("n", (1, 2, 3))
def test_tabla_monotona_extremos_y_niveles(n):
    t = H.tabla(n)
    assert len(t) == 2048 and all(a <= b for a, b in itertools.pairwise(t))
    assert t[0] == 64 and t[-1] == round(64 + 876 * H.NIVEL[n]) and max(t) <= 1023
    assert abs(t[66] - 397) <= 6          # gris 18 % ≈ 38 % de señal HLG (BT.2100)


def test_niveles_ordenados_y_comunes_bajo_la_rodilla():
    t1, t2, t3 = (H.tabla(n) for n in (1, 2, 3))
    assert t1[-1] < t2[-1] < t3[-1] and t1[:400] == t2[:400] == t3[:400]


def test_oetf_arib_puntos_conocidos():
    assert abs(H.oetf(1 / 12) - 0.5) < 1e-6 and abs(H.oetf(1.0) - 1.0) < 1e-6 and H.oetf(0) == 0


@needs_av
def test_bloque_con_el_formato_de_s_log3_y_bytes_originales():
    base, a6300 = AVCAM.read_bytes(), C.A6300.read_bytes()
    ps = C.patches(base, (C.A7S).read_bytes(), a6300, (1, 2, 3))
    C.check_base(base, ps)
    slog3 = a6300[C.u32(a6300, C.TAB_A6300 + 8 * C.SLOG3_A6300 + 4) - C.BASE:][:C.CURVE]
    for n in (1, 2, 3):
        g = 0x1B + n
        dst, blk, _ = next(p for p in ps if p[2] == f"curva 0x{g:02x} HLG{n}")
        assert len(blk) == C.CURVE == len(slog3) and blk[0x1012] == 4 and blk[0x1014] == g
        assert blk[0x1000:0x1012] == slog3[0x1000:0x1012] and blk[0x1015:] == slog3[0x1015:]
        assert struct.unpack("<2048H", blk[:0x1000]) == tuple(H.tabla(n))
        assert not any(base[dst - C.BASE:dst - C.BASE + C.CURVE])          # región a cero antes
        assert base[C.TAB["a6000"] + 8 * g + 4 - C.BASE:][:4] == b"\0" * 4  # puntero vacío antes
    assert C.HLG_REGION + 3 * C.STRIDE <= C.GAP[0] + 0x2E000 and C.HLG_REGION >= 0x43D620D9


@needs_av
def test_parche_original_sin_hlg_no_cambia():
    base = AVCAM.read_bytes()
    assert not any("HLG" in w for _, _, w in C.patches(base, C.A7S.read_bytes(), C.A6300.read_bytes()))


def test_libobj_hlg_unicorn():
    import test_g25_gamma_libobj as T
    if not T.LIB.is_file():
        pytest.skip("libObj ausente")
    old, new = T.LIB.read_bytes(), P.patch_gamma(T.LIB.read_bytes(), hlg=True)
    base = P.patch_gamma(T.LIB.read_bytes())
    for v in range(12):                                                    # lo anterior no cambia
        assert T.call(new, T.APP2OBJ_FN, 7, v) == T.call(base, T.APP2OBJ_FN, 7, v)
    for app, vid in enumerate(P.VALUEID_HLG):
        assert T.call(new, T.APP2OBJ_FN, 7, app) == (1, vid) and T.call(new, T.OBJ2APP_FN, 7, vid) == (1, app)
    assert T.call(new, T.APP2OBJ_FN, 7, 15)[0] == 0 and T.call(new, T.OBJ2APP_FN, 7, 0x589)[0] == 0
    assert len(new) == len(old)
