"""G26: parche de Color Mode de `libObj.so` (B&W, S-Gamut, S-Gamut3, S-Gamut3.Cine; valores de app 8–11 como la A6300): emulación Unicorn (offline)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
import patch_libobj_pp as P
from test_g25_gamma_libobj import APP2OBJ_FN, LIB, OBJ2APP_FN, call, needs

uc = pytest.importorskip("unicorn")


def nuevo():
    return P.patch_color(P.patch_gamma(LIB.read_bytes()))


@needs
def test_app2obj_color_acepta_12_valores_y_rechaza_el_13():
    old, new = LIB.read_bytes(), nuevo()
    for v in range(8):
        assert call(old, APP2OBJ_FN, 0, v) == (1, P.COLOR[v]) == call(new, APP2OBJ_FN, 0, v)   # 0–7 como antes
    assert call(old, APP2OBJ_FN, 0, 8)[0] == 0
    assert [call(new, APP2OBJ_FN, 0, v) for v in range(8, 12)] == [(1, 0x504), (1, 0x505), (1, 0x583), (1, 0x584)]
    assert call(new, APP2OBJ_FN, 0, 12)[0] == 0


@needs
def test_obj2app_color_es_la_inversa_y_gamma_sigue_igual():
    old, new = LIB.read_bytes(), nuevo()
    for app, vid in enumerate(P.COLOR):
        assert call(new, OBJ2APP_FN, 0, vid) == (1, app)
        if app < 8:
            assert call(old, OBJ2APP_FN, 0, vid) == (1, app)
    assert call(new, OBJ2APP_FN, 0, 0x1B7)[0] == 0 and call(new, OBJ2APP_FN, 0, 0x506)[0] == 0
    for app, vid in enumerate(P.VALUEID):                      # Gamma (G25/G26) intacta
        assert call(new, APP2OBJ_FN, 7, app) == (1, vid) and call(new, OBJ2APP_FN, 7, vid) == (1, app)


@needs
def test_camconv_color_valueid_a_byte_8():
    from unicorn import UC_HOOK_CODE, Uc, UC_ARCH_ARM, UC_MODE_THUMB
    from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R4

    def run(img, vid):
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(0, 0x1100000)
        mu.mem_write(0, img[:0x1100000])
        mu.mem_map(0x20000000, 0x1000)
        mu.reg_write(UC_ARM_REG_R0, vid)
        mu.reg_write(UC_ARM_REG_R4, 0x20000000)
        mu.hook_add(UC_HOOK_CODE, lambda u, a, s, _: u.emu_stop() if a == 0x9B32C2 else None)
        mu.emu_start(0x9B325E | 1, 0x9B32C4, count=500)
        return mu.reg_read(UC_ARM_REG_PC) & ~1, bytes(mu.mem_read(0x20000008, 1))[0]

    new = nuevo()
    for idx, vid in enumerate(P.COLOR):
        assert run(new, vid)[1] == idx
    assert run(new, 0x506)[0] == 0x9B32C4 and run(new, 0)[0] == 0x9B32C4


def test_menu_color_mode_sigue_a_la_a6300():
    import pp_menu_spec as M
    d = dict(M.COLOR_MODE_COMPLETO)
    assert [t for t, _ in M.COLOR_MODE_COMPLETO] == ["Movie", "Still", "Cinema", "Pro", "ITU709 Matrix", "Black & White", "S-Gamut", "S-Gamut3.Cine", "S-Gamut3"]
    assert (P.COLOR[d["Black & White"]], P.COLOR[d["S-Gamut"]], P.COLOR[d["S-Gamut3"]], P.COLOR[d["S-Gamut3.Cine"]]) == (0x504, 0x505, 0x583, 0x584)
    assert [d[k] for k in ("Movie", "Still", "Cinema", "Pro", "ITU709 Matrix")] == [dict(M.SETTINGS["color_mode"].opciones)[k] for k in ("Movie", "Still", "Cinema", "Pro", "ITU709 Matrix")]


@needs
def test_bw_envia_movie_y_saturacion_menos_8():
    """G27: el núcleo de la A6000 no conoce el tipo 8; su B&W es saturación < −7 (indicador monocromo, `av-cam 0x437a273c`)."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R4

    def run(img, tipo, sat):
        mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        mu.mem_map(0, 0x1100000)
        mu.mem_write(0, img[:0x1100000])
        mu.mem_map(0x20000000, 0x1000)
        mu.mem_write(0x20000008, bytes([tipo]))
        mu.reg_write(UC_ARM_REG_R0, sat & 0xFFFFFFFF)
        mu.reg_write(UC_ARM_REG_R4, 0x20000000)
        mu.hook_add(UC_HOOK_CODE, lambda u, a, s, _: u.emu_stop() if a == P.SAT_SIGUE else None)
        mu.emu_start(P.SAT_SITE | 1, P.SAT_SIGUE + 2, count=50)
        m = bytes(mu.mem_read(0x20000000, 0x20))
        return m[8], m[0x15]

    old, new = nuevo(), P.patch_bw(nuevo())
    assert run(new, 8, 3) == (5, 0xF8)                                   # B&W → Movie + saturación −8
    for tipo in (0, 5, 7, 9, 11):
        for sat in (-8, 0, 7):
            assert run(new, tipo, sat) == run(old, tipo, sat) == (tipo, sat & 0xFF)
    with pytest.raises(AssertionError):
        P.patch_bw(P.patch_gamma(LIB.read_bytes()))                      # exige patch_color (usa su hueco)
