"""G71 — LUT 3D: empaquetador/generador del `av-cam` (Unicorn), herramienta de descomposición y parche de carga."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui")]
import cube_a6000 as C
import lut3d_emu as E
import lut_patch as P

IMG = C.BIN.read_bytes()


def test_ganchos_originales_y_zona_a_cero():
    for va, old, _, _ in P.HOOKS:
        assert IMG[va - P.BASE:va - P.BASE + 4] == old
    assert not any(IMG[P.CODE - P.BASE:P.TABLES + 3 * P.TAM - P.BASE])


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
    for k in (0, 1):
        assert P.emular(parcheada, k, 0) == 0x11223344
        assert P.emular(parcheada, k, 9) == 0x11223344           # fuera de opciones = Off
        for o in (1, 2, 3):
            assert P.emular(parcheada, k, o) == P.TABLES + (o - 1) * P.TAM


def test_lut1_escribe_la_tabla_correcta(parcheada):
    t = P.tablas_por_defecto()
    assert parcheada[P.TABLES - P.BASE:P.TABLES - P.BASE + P.TAM] == t[0]
    assert any(t[0]) and not any(t[2])                          # LUT3 = identidad = ceros


def test_parche_solo_toca_ganchos_y_zona(parcheada):
    dif = [i + P.BASE for i in range(len(IMG)) if IMG[i] != parcheada[i]]
    assert all(P.CODE <= a < P.TABLES + 3 * P.TAM or any(h[0] <= a < h[0] + 4 for h in P.HOOKS) for a in dif)


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
    assert [o[0] for o in cfw.POR_ID["lut"].opciones] == ["Off", "LUT1", "LUT2", "LUT3"]
    assert len({a.backup for a in cfw.AJUSTES}) == len(cfw.AJUSTES) == 10
