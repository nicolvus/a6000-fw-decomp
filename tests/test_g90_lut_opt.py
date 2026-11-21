"""G90 — interpolación (A), optimización en ΔE (B), geometría del bloque LUT (C)."""
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C
import exp_interp as E
import lut_opt as O
import lut_sd_userland as SD

BANCOS = [75, 60, 60, 48, 50, 40, 40, 32]       # palabras por SRAM (0x43b67918: 0x12c, 0xf0, 0xf0, 0xc0, 0xc8, 0xa0, 0xa0, 0x80 B)


def test_perm_es_8_bancos_por_paridad():
    """C: la escritura al HW son 8 bloques fijos y la permutación agrupa los nodos por paridad (j, a, b) en ese orden."""
    img = C.BIN.read_bytes()
    perm = struct.unpack_from("<405H", img, C.PERM - C.BASE)
    orden = [(j, a, b) for j in (0, 1) for a in (0, 1) for b in (0, 1)]
    ini = 0
    for pb, n in zip(orden, BANCOS):
        pos = sorted(perm[j * 81 + a * 9 + b] for j in range(5) for a in range(9) for b in range(9) if (j % 2, a % 2, b % 2) == pb)
        assert pos == list(range(ini, ini + n))
        ini += n
    assert ini == 405


def test_tetra_exacta_en_afines_y_en_nodos():
    rng = np.random.default_rng(3)
    u = np.column_stack([rng.random(500), rng.random(500) - .5, rng.random(500) - .5])
    idx, w = O.pesos_tetra(u)
    assert np.allclose(w.sum(1), 1) and (w >= -1e-12).all()
    nodo = np.array([[(i // 81) / 4, (i // 9 % 9 - 4) / 8, (i % 9 - 4) / 8] for i in range(405)])
    assert np.allclose(np.einsum("mk,mkc->mc", w, nodo[idx]), u)          # reproduce funciones afines
    j, w2 = O.pesos_tetra(nodo)
    assert np.allclose(np.einsum("mk,mk->m", w2, (j == np.arange(405)[:, None]).astype(float)), 1)


def test_exp_interp_decide_cada_modelo():
    t = np.linspace(-1, 1, 41)
    rng = np.random.default_rng(1)
    for modelo, veredicto in (("tri", "trilineal"), ("tetra", "tetraedrica")):
        med = {n: (t, E.respuesta(d, t, modelo) + rng.normal(0, 0.002, 41)) for n, (d, _) in E.RAMPAS.items()}
        assert E.decide(med)["veredicto"] == veredicto


def test_ajuste_de_mejora_al_lsq_y_ambos_acota():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.cube"
        C.escribe_cube(p, C.lut_teal_orange, 17, "x")
        tab, lo, hi = C.lee_cube(p)
    f = lambda x: C.aplica_cube(tab, lo, hi, x)
    ch = C.Cadena()
    xt, w = O.muestras(n_unif=4000)
    c, y = ch.pre_lut(xt), f(xt)
    xe = np.random.default_rng(7).random((6000, 3))
    ce, ye = ch.pre_lut(xe), f(xe)
    u = C.rgb2ycc(c)
    q_old, _ = C.a_unidades(C.ajusta_lut3d(u, C.rgb2ycc(y) - u))
    q_new = O.ajusta_de(c, y, w, "tri", iters=2, pasadas=2)
    e = lambda q, m: C.de2000(ye, np.clip(O.aplica(q, ce, m), 0, 1)).mean()
    assert e(q_new, "tri") < 0.85 * e(q_old, "tri")
    assert q_new.min() >= -64 and q_new.max() <= 63


def test_lutsd_correccion_baja_el_error_en_pelicula():
    """B (cámara): la 2.ª diferencia de lutsd.c/`referencia` mejora el muestreo directo (se mide con la tabla que de verdad sale del blob)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "t.cube"
        C.escribe_cube(p, C.lut_pelicula, 17, "x")
        texto = p.read_text()
        tab, lo, hi = C.lee_cube(p)
    f = lambda x: C.aplica_cube(tab, lo, hi, x)
    bits = int.from_bytes(SD.referencia(texto), "little")
    sg = lambda v: v - 128 if v & 64 else v
    q = np.array([[sg(bits >> (21 * i + s) & 127) for s in (14, 7, 0)] for i in range(405)], np.int8)
    xe = np.random.default_rng(7).random((6000, 3))
    ch = C.Cadena()
    ce, ye = ch.pre_lut(xe), f(xe)
    assert C.de2000(ye, np.clip(O.aplica(q, ce, "tri"), 0, 1)).mean() < 1.2       # muestreo directo: 1,44 (g90 §B)
