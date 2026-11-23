"""G96 — modelo paramétrico de películas: sin parámetros es la identidad y cada película conserva los grises casi neutros y el orden de luminancia."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/lut"))
import peliculas as F


def test_pelicula_neutra_es_identidad():
    x = np.random.default_rng(0).random((500, 3))
    assert np.allclose(F.Pelicula("id")(x), x, atol=1e-9)


def test_grises_monotonos_y_casi_neutros():
    g = np.repeat(np.linspace(0, 1, 33)[:, None], 3, 1)
    for p in F.PELICULAS:
        y = p(g)
        assert np.all(np.diff(y.mean(1)) > 0), p.nombre
        assert np.abs(y - y.mean(1, keepdims=True)).max() < 0.1, p.nombre          # dominante buscada (Gold: luces amarillas ≈ 0,08)
