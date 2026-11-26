"""G71 — LUT 3D: empaquetador/generador del `av-cam` (Unicorn), herramienta de descomposición y parche de carga.
G116: el ajuste es solo SD (tabla del blob 0x150005) y cueva/máquina/curva viven en el hueco G18 (`ZONA_L18`/`ZONA_T18`), no en `ZONA_A`/`ZONA_B`."""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui")]
import avcam_dinamico as D
import cube_a6000 as C
import lut3d_emu as E
import lut_patch as P
import lut_sd_userland as U
import lut_t as TT

IMG = C.BIN.read_bytes()
TABLAS = {k: bytes((i * 37 + k) % 256 for i in range(D.LUT_BYTES)) for k in range(1, 4)}


def test_ganchos_originales_y_zonas_libres_a_cero():
    for va, old, _, _ in P.HOOKS:
        assert IMG[va - P.BASE:va - P.BASE + 4] == old
    for z in (D.ZONA_L18, TT.ZONA_T18):
        assert not any(IMG[z[0] - P.BASE:z[1] - P.BASE])


def test_empaquetador_y_generador_coinciden_con_empaqueta_hw():
    rng = np.random.default_rng(3)
    q = rng.integers(-64, 64, (405, 3)).astype(np.int8)
    ref = bytes(q[:, 0].astype(np.uint8)) + bytes(q[:, 1].astype(np.uint8)) + bytes(q[:, 2].astype(np.uint8))
    assert E.generar(ref) == C.empaqueta_hw(q, IMG)


def test_tabla_cero_es_identidad_de_fabrica():
    assert not any(E.generar(bytes(1215)))


def test_permutacion_valida():
    assert sorted(E.perm(IMG)) == list(range(405))


@pytest.fixture(scope="module")
def parcheada():
    return P.apply_bytes(IMG)


def test_off_igual_que_fabrica_y_lut_elige_la_tabla_del_blob(parcheada):
    blob, perm = U.blob_tablas(TABLAS), list(struct.unpack_from("<405H", IMG, D.PERM - P.BASE))
    for k in (0, 1):
        assert P.emular(parcheada, k, 0, blob)[0] == 0x11223344
        assert P.emular(parcheada, k, 9, blob)[0] == 0x11223344   # fuera de opciones = Off
        for o in (1, 2, 3):
            assert P.emular(parcheada, k, o, blob)[:2] == (0x31000000, D.desempaqueta_21(TABLAS[o], perm))
        assert P.emular(parcheada, k, 1, bytes(U.BK_TAM))[0] == 0x11223344   # sin SD = fábrica


def test_reserva_una_vez_y_fallo_cae_a_fabrica(parcheada):
    blob = U.blob_tablas(TABLAS)
    assert P.emular(parcheada, 0, 2, blob)[2]["mallocs"] == [0x654, U.BK_TAM]
    assert P.emular(parcheada, 1, 0, blob)[2] == {"mallocs": [], "lecturas": [P.AJ_SD.backup]}   # Off no reserva ni lee el blob
    for k in (0, 1):
        assert P.emular(parcheada, k, 1, blob, malloc_falla_en=1)[0] == 0x11223344    # sin búfer del ISP: puntero original
        assert P.emular(parcheada, k, 1, blob, malloc_falla_en=2)[0] == 0x11223344    # sin búfer del blob: puntero original


def test_empaquetado_21_bits_sin_perdida():
    perm = list(struct.unpack_from("<405H", IMG, D.PERM - P.BASE))
    q = np.random.default_rng(4).integers(-64, 64, (405, 3)).astype(np.int8)
    hw = C.empaqueta_hw(q, IMG)
    t = D.empaqueta_21(hw, perm)
    assert len(t) == D.LUT_BYTES == 1064 and D.desempaqueta_21(t, perm) == hw


def test_parche_solo_toca_ganchos_y_zonas_verificadas(parcheada):
    """G116: cueva, máquina y curva van al hueco G18 (`ZONA_L18`/`ZONA_T18`); `ZONA_A` (tabla T1) y `ZONA_B` (BOKS) quedan intactas."""
    dif = [i + P.BASE for i in range(len(IMG)) if IMG[i] != parcheada[i]]
    zonas = (D.ZONA_L18, TT.ZONA_T18)
    ganchos = [h[0] for h in (*P.HOOKS, P.HOOK_MAQ)] + list(TT.SITIOS_T)
    assert all(any(z[0] <= a < z[1] for z in zonas) or any(h <= a < h + 4 for h in ganchos) for a in dif)
    assert not any(0x43D620D9 <= a < 0x43FA8F00 for a in dif)   # nada en la zona viva de G72
    assert not any(any(z[0] <= a < z[1] for z in (D.ZONA_A, D.ZONA_B)) for a in dif)   # ni en T1/BOKS
    assert TT.ZONA_T18[0] >= D.ZONA_G18[0] and TT.ZONA_T18[1] <= D.ZONA_G18[1]


def test_cube_ida_y_vuelta(tmp_path):
    C.escribe_cube(tmp_path / "a.cube", C.lut_teal_orange, 17, "t")
    tab, lo, hi = C.lee_cube(tmp_path / "a.cube")
    x = np.random.default_rng(1).random((500, 3))
    assert np.abs(C.aplica_cube(tab, lo, hi, x) - np.clip(C.lut_teal_orange(x), 0, 1)).max() < 0.02


def test_descomposicion_mejora_y_identidad_no_empeora():
    x = np.random.default_rng(2).random((4000, 3))
    base = C.error(C.lut_teal_orange, C.Cadena(), x)[0]
    assert C.error(C.lut_teal_orange, C.descompone(C.lut_teal_orange, False, False, True), x)[0] < base / 3
    assert C.error(C.lut_identidad, C.descompone(C.lut_identidad, False, False, True), x)[0] < 0.5


def test_ajuste_lut_en_cfw_ajustes():
    import cfw_ajustes as cfw
    assert [o[0] for o in cfw.POR_ID["lut"].opciones] == ["Off", "Teal&Orange", "Película", "Neutro"]
    assert len({a.backup for a in cfw.AJUSTES}) == len(cfw.AJUSTES)


def test_hlg_y_lut_no_se_solapan_ni_tocan_zonas_prohibidas():
    import pp_curves_patch as PC
    if not PC.A6300.is_file():
        pytest.skip("A6300 ausente")
    perm = list(struct.unpack_from("<405H", IMG, D.PERM - P.BASE))
    cueva, _ = D.lut_codigo(P.AJ_SD, P.HOOKS)
    esc = [(a, a + len(b)) for a, b in cueva] + [(D.LUT_CELDA, D.LUT_CELDA + 8)]
    D.comprobar_zonas(esc, (D.ZONA_L18, TT.ZONA_T18))          # la LUT, en su hueco
    h = D.hlg_parches(PC.A6300.read_bytes(), PC.TAB_A6300, PC.SLOG3_A6300)
    h_lo, h_hi = h[0][0], h[0][0] + len(h[0][1])               # HLG sigue con su cueva en ZONA_A (fuera de este cambio)
    assert not any(h_lo < hi and lo < h_hi for lo, hi in esc), "HLG y LUT se solapan"
    assert len(perm) == 405
