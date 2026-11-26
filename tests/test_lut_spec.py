"""G114 — validador de `.cube` antes de pasarlo a la cámara (`scripts/lut/cube_spec.py`)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_spec as S


def _cube(tmp_path, n=2, fn=None, cabecera="", nombre="a.cube"):
    fn = fn or (lambda r, g, b: (r * 0.9 + 0.05, g * 0.9 + 0.05, b * 0.9 + 0.05))
    filas = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                filas.append(fn(i / (n - 1), j / (n - 1), k / (n - 1)))
    txt = f'TITLE "prueba"\n{cabecera}LUT_3D_SIZE {n}\n'
    txt += "".join(f"{r:.6f} {g:.6f} {b:.6f}\n" for r, g, b in filas)
    p = tmp_path / nombre
    p.write_text(txt)
    return p


def test_valido(tmp_path):
    s, err, av = S.valida(_cube(tmp_path, 17))
    assert not err and not av, (err, av)
    assert (s.n, s.filas, s.identidad, s.entrada_log) == (17, 17**3, False, False)
    assert S.apta(s, err) == "HARDWARE"


def test_identidad_se_detecta(tmp_path):
    s, err, _ = S.valida(_cube(tmp_path, 4, lambda r, g, b: (r, g, b)))
    assert not err and s.identidad


def test_filas_incompletas(tmp_path):
    p = _cube(tmp_path, 3)
    lineas = p.read_text().splitlines()
    p.write_text("\n".join(lineas[:-1]) + "\n")
    _, err, _ = S.valida(p)
    assert any("esperadas 27" in e for e in err)


def test_1d_y_uniforme(tmp_path):
    s, err, _ = S.valida(_cube(tmp_path, 3, cabecera="LUT_1D_SIZE 2\n"))
    assert s.tiene_1d and S.apta(s, err) == "SOLO SOFTWARE"
    s, err, _ = S.valida(_cube(tmp_path, 3, lambda r, g, b: (b, b, b)))
    assert s.uniforme and S.apta(s, err) == "SOLO SOFTWARE"


def test_rango_y_dominio(tmp_path):
    _, err, _ = S.valida(_cube(tmp_path, 3, lambda r, g, b: (r, g, b * 2)))
    assert err  # valores fuera de 0…1
    _, err, _ = S.valida(
        _cube(tmp_path, 3, cabecera="DOMAIN_MIN 0 0 1\nDOMAIN_MAX 1 1 0\n")
    )
    assert any("incoherentes" in e for e in err)


def test_nan_y_tamano(tmp_path):
    _, err, _ = S.valida(_cube(tmp_path, 2, lambda r, g, b: (r, float("nan"), b)))
    assert any("NaN" in e for e in err)
    assert any("fuera de 2…129" in e for e in S.valida(_cube(tmp_path, 130))[1])


def test_vlog_frente_a_std(tmp_path):
    s, _, av = S.valida(_cube(tmp_path, 3, cabecera="#LUMIXPHOTOSTYLE VLOG\n"))
    assert s.entrada_log and any("logarítmica" in a for a in av)
    s, _, av = S.valida(_cube(tmp_path, 3, cabecera="#LUMIXPHOTOSTYLE STD\n"))
    assert not s.entrada_log and not any("logarítmica" in a for a in av)


def test_limites_del_lector_de_la_camara(tmp_path):
    p = _cube(tmp_path, 65)
    _s, _, av = S.valida(p)
    assert any("no cabe en el lector" in a for a in av)
    p = _cube(tmp_path, 3)
    p.write_text(p.read_text() + "# " + "x" * 120 + "\n")
    _s, _, av = S.valida(p)
    assert any("corta en 95" in a for a in av)


def test_fichero_inexistente(tmp_path):
    _, err, _ = S.valida(tmp_path / "no.cube")
    assert err and err[0].startswith("no se puede leer")
