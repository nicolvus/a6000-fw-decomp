"""G92 — ranura libre de la cadena de tono (`c68[8]`) ejecutada con Unicorn sobre `av-cam` real."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C
import tono_post as P

pytestmark = pytest.mark.skipif(not P.BIN.exists(), reason="falta av-cam.bin")
G = 1                                           # gamma con puntero en la imagen (entrada 2)


@pytest.fixture(scope="module")
def img():
    return P.BIN.read_bytes()


def test_ranuras_libres_son_identidad(img):
    ptr = [P._u32(img, P.TAB_C68 + 4 * i) for i in range(14)]
    assert [i for i, p in enumerate(ptr) if p == P.IDENTIDAD] == [0, 6, 8, 9, 10, 11, 12, 13]
    ident = np.frombuffer(img[P.IDENTIDAD - P.BASE:P.IDENTIDAD - P.BASE + 2048], "<u2")
    assert np.array_equal(ident[:1023], np.arange(1023)) and ident[1023] == 1023


def test_cadena_aplica_T_tras_la_gamma(img):
    x = np.arange(512) * 4
    g = P.gamma(img, G)
    assert np.array_equal(P.emula(img, G, bd5=0), g[x])                       # sin efecto: gamma sola
    assert np.array_equal(P.emula(img, G), g[x])                              # ranura 8 de fábrica = identidad
    T = np.clip(np.round(1023 * (np.arange(1024) / 1023) ** 1.6), 0, 1023)
    assert np.array_equal(P.emula(img, G, T), T[np.minimum(g[x], 1023)].astype(int))


def test_black_gamma_tiene_prioridad(img):
    T = np.full(1024, 512)
    assert np.array_equal(P.emula(img, G, T, bd1=1), P.emula(img, G, bd5=0, bd1=1))


def test_curva_post_de_una_cadena():
    ch = C.descompone(C.lut_pelicula, usa_M=False, usa_T=True, usa_L=False)
    t = P.curva_post(ch)
    assert t.dtype == np.uint16 and len(t) == 1024 and np.all(np.diff(t.astype(int)) >= 0)
    v = np.linspace(0, 1, 9)
    assert np.allclose(t[np.round(v * 1023).astype(int)] / 1023, ch.pre_lut(np.repeat(v[:, None], 3, 1))[:, 0], atol=2 / 1023)
