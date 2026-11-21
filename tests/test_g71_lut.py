"""G71 — LUT 3D: empaquetador/generador del `av-cam` (Unicorn), herramienta de descomposición y parche de carga."""
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

IMG = C.BIN.read_bytes()


def test_ganchos_originales_y_zona_a_cero():
    for va, old, _, _ in P.HOOKS:
        assert IMG[va - P.BASE:va - P.BASE + 4] == old
    for z in (D.ZONA_A, D.ZONA_B):
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


def test_off_igual_que_fabrica_y_lut_elige_tabla(parcheada):
    t = P.tablas_por_defecto()
    for k in (0, 1):
        assert P.emular(parcheada, k, 0) == 0x11223344
        assert P.emular(parcheada, k, 9) == 0x11223344           # fuera de opciones = Off
        for o in (1, 2, 3):
            assert P.emular(parcheada, k, o) == 0x30001000
            assert P.emular.mem == t[o - 1]                      # desempaquetado = tabla original, byte a byte


def test_reserva_una_vez_y_fallo_cae_a_fabrica(parcheada):
    n = [0]
    P.emular(parcheada, 0, 2, cuenta=n)
    assert n == [1]
    P.emular(parcheada, 1, 0, cuenta=n)
    assert n == [0]                                              # Off no reserva
    for k in (0, 1):
        for o in (1, 2, 3):
            assert P.emular(parcheada, k, o, malloc=0, cuenta=n) == 0x11223344 and n == [1]   # malloc = 0 → puntero original


def test_empaquetado_21_bits_sin_perdida():
    perm = list(struct.unpack_from("<405H", IMG, D.PERM - P.BASE))
    t = P.tablas_por_defecto()[0]
    assert len(D.empaqueta_21(t, perm)) == D.LUT_BYTES == 1064 and 3 * D.LUT_BYTES + 3 <= D.ZONA_B[1] - D.ZONA_B[0]


def test_parche_solo_toca_ganchos_y_zonas_verificadas(parcheada):
    dif = [i + P.BASE for i in range(len(IMG)) if IMG[i] != parcheada[i]]
    assert all(D.ZONA_A[0] <= a < D.ZONA_A[1] or D.ZONA_B[0] <= a < D.ZONA_B[1] or any(h[0] <= a < h[0] + 4 for h in (*P.HOOKS, P.HOOK_MAQ)) for a in dif)
    assert not any(0x43D620D9 <= a < 0x43FA8F00 for a in dif)   # nada en la zona viva de G72


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
    cueva, _ = D.lut_codigo(P.AJ, P.HOOKS)
    esc = [(a, a + len(b)) for a, b in cueva] + [(D.LUT_TABLAS, D.LUT_TABLAS + 3 * D.LUT_BYTES), (D.LUT_CELDA, D.LUT_CELDA + 4)]
    h = D.hlg_parches(PC.A6300.read_bytes(), PC.TAB_A6300, PC.SLOG3_A6300)
    esc.append((h[0][0], h[0][0] + len(h[0][1])))
    D.comprobar_zonas(esc)
    assert len(perm) == 405
