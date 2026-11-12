"""T9 — ISP emulado: tablas extraídas, modelo CPU, ids de Backup de PP, ΔE y (si hay Chromium) shader = CPU."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/isp"))
import compara_real as C
import extrae_tablas as X
import modelo as M
import valida_curvas as V

T = M.Tablas()


def test_curvas_monotonas_y_de_10_bits() -> None:
    assert len(T.curvas) >= 80
    for k, c in T.curvas.items():
        assert c.shape == (2048,) and (np.diff(c.astype(int)) >= 0).all(), k
        assert c.max() < 2048, k


@pytest.mark.skipif(not X.BINS["a6000"][0].is_file() or not X.BINS["a7s"][0].is_file(), reason="faltan av-cam.bin")
def test_extraccion_reproduce_el_npz_y_la_curva_movie_es_igual_en_a6000_y_a7s() -> None:
    arr, _ = X.extrae_curvas()
    assert all(np.array_equal(arr[k], v) for k, v in T.curvas.items())
    assert np.array_equal(T.curvas["a6000_v0a"], T.curvas["a7s_v0a"])   # G16: curvas de vídeo comunes idénticas


def test_matrices_neutras_y_movie() -> None:
    assert np.allclose(T.matrices.sum(2), 1.0)
    assert (T.matrices[0] * 1024).round().astype(int).ravel().tolist() == [1292, -180, -88, -44, 1340, -272, -24, -108, 1156]   # G27 §5
    assert np.allclose(T.matrices[14], np.eye(3))


def test_slog3_de_la_a6300_coincide_con_la_formula_publica() -> None:
    e, k = V.ajusta(T.curvas["a6300_v1f"] / 1023.0, V.slog3)
    assert e < 0.003 and 5.3 < k < 5.7


def test_lut_cpu_en_puntos_de_control() -> None:
    c = T.curvas["a6000_v0a"] / 1023.0
    x = np.array([0, 1 / 2047, 64 / 2047, 0.5 / 2047, 1.0, 2.0])
    r = M.lut(c, x)
    assert np.allclose(r[:3], c[[0, 1, 64]]) and np.isclose(r[3], (c[0] + c[1]) / 2) and r[4] == r[5] == c[-1]


def test_aplica_negro_blanco_y_saturacion_menos_8_es_blanco_y_negro() -> None:
    px = np.array([[[0, 0, 0], [1, 1, 1], [0.8, 0.3, 0.2]]], float)
    o = M.aplica(px, {"gamma": 4}, T, exposicion=1.0)
    assert o[0, 0].max() < 0.02 and o[0, 1].min() > 0.99
    bn = M.aplica(px, {"gamma": 4, "saturation": -8}, T, exposicion=1.0)[0, 2]
    assert np.ptp(bn) < 1e-6


def test_ids_de_backup_de_pp() -> None:
    ids = T.pp_ids
    assert len(ids) == 11 and all(len(f) == 31 for f in ids) and len({i for f in ids for i in f}) == 341
    assert ids[0][7] == 0x10701EA and ids[4][0] == 0x107062B and ids[10][0] == 0x1070631    # G36
    ops = M.nvram_ops(T, 0, {"gamma": 6, "phase": -3})
    assert ops == {0x10701EA: b"\x06", ids[0][30]: b"\xfd"}
    assert M.ajustes_desde_nvram(T, 0, ops) == {"gamma": 6, "phase": -3}
    with pytest.raises(ValueError):
        M.nvram_ops(T, 0, {"gamma": 99})


def test_delta_e_identidad_y_blanco() -> None:
    a = np.random.default_rng(0).random((8, 8, 3))
    assert C.delta_e(a, a)["dE76_media"] == 0
    assert np.allclose(C.lab(np.ones((1, 1, 3)))[0, 0], [100, 0, 0], atol=0.2)


def test_ganancia_por_bandas() -> None:
    g = M.ganancia_filas([1, 2], 4)
    assert g[0] == 1 and g[-1] == 2 and (np.diff(g) >= 0).all() and (M.ganancia_filas(None, 3) == 1).all()


def test_shader_igual_que_cpu() -> None:
    r = subprocess.run([sys.executable, str(ROOT / "scripts/gui/isp/prueba_shader.py"), "--puerto", "8605"], check=False, capture_output=True, text=True, timeout=180)
    if r.returncode == 2:
        pytest.skip("sin Chromium headless")
    assert r.returncode == 0, r.stdout[-500:]
