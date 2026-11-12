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
import raw_entrada as R
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
    assert all(np.array_equal(arr[k], v) for k, v in T.curvas.items() if k != "sr2_std")   # sr2_std viene de los ARW, no de av-cam
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


ARW = Path.home() / "Desktop/16161111/DSC03773.ARW"   # material real del usuario (no versionado)
LIBOBJ = ROOT / "analysis/camera-extract/usr/lib/libObj.so"


def test_descifrado_sony_es_involutivo_y_el_estandar_coincide_con_backup() -> None:
    x = bytes(range(256)) * 4
    assert R.descifra_sony(R.descifra_sony(x, 1144201745), 1144201745) == x != R.descifra_sony(x, 1)
    import json
    j = json.loads((M.DIR / "sr2_standard.json").read_text())
    c = np.array(j["curva_0x7802"])
    assert len(c) == 512 and (np.diff(c) >= 0).all() and c.max() == 1023 and j["negro_0x7310"] == [512] * 4
    assert (T.matrices[0] * 1024).round().astype(int).ravel().tolist() == j["matriz_0x7800"]   # SR2 de los ARW = matriz de Backup 0 (REAL)
    assert M.CURVA_FOTO[5] in T.curvas and T.curvas["sr2_std"].shape == (2048,)


@pytest.mark.skipif(not ARW.is_file(), reason="sin el ARW de e26-r85")
def test_sr2_de_un_arw_real_y_alineacion() -> None:
    s = R.sr2(ARW.read_bytes())
    assert s[0x7313].tolist() == [3148, 1024, 1024, 1644] and s[0x7310].tolist() == [512] * 4 and s[0x7802].shape == (512,) and sum(s[0x7800][:3]) == 1024
    p = np.array([0, 0, 1, 0, 0.])
    sx, sy = R.mapas(p, 40, 30, 40, 30)
    assert np.allclose(sx, np.arange(40)[None, :], atol=1e-3) and np.allclose(sy, np.arange(30)[:, None], atol=1e-3)


def test_curva_pp_como_el_cfw() -> None:
    base = T.curvas["a6000_v0a"].astype(int)
    q = {**M.NEUTRO}
    assert (M.curva_pp(base, 4, q) == base).all()                          # neutro: curva intacta
    up = M.curva_pp(base, 4, {**q, "black_level": 15})
    assert up[0] == 94 and up[-1] == base[-1] and (np.diff(up) >= 0).all()   # pp_tone.c: y += 6·nivel·(top−y)/top → y[0] de 5 a 94, blanco intacto (G33 §4 cita 64 con 4·: texto anterior al código)
    k = M.curva_pp(base, 4, {**q, "knee_mode": 1, "knee_point": 0, "knee_slope": 0})
    pt = 1023 * 750 // 1000
    assert (k[base <= pt] == base[base <= pt]).all() and k[-1] < base[-1] and (k[base > pt] >= pt).all()   # solo comprime por encima del punto
    assert (M.curva_pp(base, 11, {**q, "bg_level": 7, "knee_mode": 1, "knee_point": 0}) == base).all()       # log: sin Black Gamma ni rodilla
    assert M.curva_pp(base, 4, {**q, "bg_level": 7})[100] > base[100] > M.curva_pp(base, 4, {**q, "bg_level": -7})[100]


def test_gammas_10_y_11_resueltas_con_bytes_y_forma() -> None:
    assert (M.CURVA_VIDEO[10], M.CURVA_VIDEO[11]) == ("a7s_v1d", "a7s_v1c")
    X_ = V.X
    for k, f in (("a7s_v1c", V.slog2), ("a7s_v16", V.r709)):                # 0x1c = S-Log2 y 0x16 = BT.709 (afín, k libre): RMSE < 1e-3
        c = T.curvas[k] / 1023.0
        e = min(np.sqrt(np.mean((np.linalg.lstsq(np.stack([g := f(X_[8:] * kk), np.ones_like(g)], 1), c[8:], rcond=None)[0] @ np.stack([g, np.ones_like(g)]) - c[8:]) ** 2)) for kk in np.geomspace(0.2, 40, 200))
        assert e < 1e-3, (k, e)


@pytest.mark.skipif(not LIBOBJ.is_file(), reason="sin libObj.so")
def test_camMsgConv_original_manda_0x480_al_selector_10_y_0x481_al_11() -> None:
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    d = LIBOBJ.read_bytes()
    ins = {i.address: f"{i.mnemonic} {i.op_str}" for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(d[0x9B3728:0x9B3770], 0x9B3728)}
    assert ins[0x9B3728] == "cmp.w r0, #0x480" and ins[0x9B372C] == "beq #0x9b3768" and ins[0x9B3768] == "movs r3, #0xa"
    assert ins[0x9B372E] == "movw r3, #0x481" and ins[0x9B3734] == "beq #0x9b376c" and ins[0x9B376C] == "movs r3, #0xb"


def test_dro_y_detalle_en_cpu() -> None:
    assert M.dro_auto_k(np.full((2, 2, 3), 0.001)) == pytest.approx(1.46) and M.dro_auto_k(np.full((2, 2, 3), 0.9)) == pytest.approx(0.66)
    plano = np.full((4, 4, 3), 0.5)
    assert np.allclose(M.aplica(plano, {"det_level": 7}, T), M.aplica(plano, {}, T))
    borde = np.concatenate([np.full((4, 4, 3), 0.2), np.full((4, 4, 3), 0.7)], 1)
    assert M.aplica(borde, {"det_level": 7}, T)[1, 3].mean() < M.aplica(borde, {}, T)[1, 3].mean()   # halo a ambos lados del borde


def test_conjunto_de_deltas_como_av_cam_0x437a44d0() -> None:
    d = bytearray(0x600)
    d[0x100 + 7 * 24:0x100 + 8 * 24] = bytes(range(1, 25))       # conjunto 7 (Standard, +0x7b)
    d[0x480:0x480 + 24] = b"\xff" * 24                           # conjunto 0xe = −1 (int8)
    base = list(range(10, 18))
    v = M.conjunto_deltas(bytes(d), 7, base)
    assert v.shape == (3, 8) and v.dtype == np.int16
    assert v[0].tolist() == [b + s for b, s in zip(base, range(1, 9))]
    assert v[1].tolist() == (v[0] + np.arange(9, 17)).tolist() and v[2].tolist() == (v[0] + np.arange(17, 25)).tolist()
    assert M.conjunto_deltas(bytes(d), 0xE, [0] * 8)[2].tolist() == [-2] * 8
    with pytest.raises(ValueError):
        M.conjunto_deltas(bytes(d), 0x19, base)


def test_tono4_neutro_en_grises_y_activo_solo_en_foto() -> None:
    gris = np.full((2, 2, 3), 0.4)
    assert np.allclose(M.tono4(gris), gris, atol=1e-6)
    rojo = np.array([[[0.8, 0.2, 0.2]]])
    assert not np.allclose(M.tono4(rojo), rojo, atol=1e-3)
    lin = np.full((2, 2, 3), 0.05)
    lin[0, 0] = (0.2, 0.02, 0.02)
    assert not np.allclose(M.aplica(lin, {"gamma": 5}, T, True, 1.0, True), M.aplica(lin, {"gamma": 5}, T, True, 1.0, True, tono=False))
    assert np.allclose(M.aplica(lin, {}, T, False, 1.0, True), M.aplica(lin, {}, T, False, 1.0, True, tono=False))   # vídeo/shader: sin cambio
