"""G88 — LUTs propios desde `.cube` (32³ incl.): parser, conversión a las tablas del ISP, ΔE frente al .cube exacto, nombres en la opción «LUT» y selección en las cuevas reales (Unicorn)."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui")]
import cfw_ajustes
import cube_a6000 as C
import lut_patch as P
import sd_lut as S


def curva_tono(x):
    """Gamma 0,8 + tinte frío en sombras y cálido en luces (curva y tono conocidos)."""
    y = np.clip(x, 0, 1) ** 0.8
    lum = y.mean(-1, keepdims=True)
    return np.clip(y + (lum - 0.5) * np.array([0.10, 0.0, -0.10]), 0, 1)


@pytest.fixture(scope="module")
def carpeta(tmp_path_factory):
    d = tmp_path_factory.mktemp("cubes")
    C.escribe_cube(d / "Fuji32.cube", curva_tono, 32, "t")
    C.escribe_cube(d / "Pelicula17.cube", C.SINT["pelicula"], 17, "t")
    C.escribe_cube(d / "TealOrangeLargo33.cube", C.SINT["teal_orange"], 33, "t")
    return d


@pytest.fixture(scope="module")
def conv(carpeta):
    return S.convierte(S.lee_cubes(carpeta))


@pytest.mark.parametrize("n", [17, 32, 33, 64])
def test_parser_acepta_tamanos(tmp_path, n):
    C.escribe_cube(tmp_path / "a.cube", C.SINT["pelicula"], n, "t")
    tab, lo, hi = C.lee_cube(tmp_path / "a.cube")
    assert tab.shape == (n, n, n, 3)
    x = np.random.default_rng(1).random((500, 3))
    assert np.abs(C.aplica_cube(tab, lo, hi, x) - C.SINT["pelicula"](x)).max() < 0.03 if n >= 32 else True


def test_cube_invalido(tmp_path):
    (tmp_path / "m.cube").write_text("LUT_3D_SIZE 4\n0 0 0\n")
    with pytest.raises(ValueError):
        C.lee_cube(tmp_path / "m.cube")
    (tmp_path / "u.cube").write_text("LUT_1D_SIZE 4\n")
    with pytest.raises(ValueError):
        C.lee_cube(tmp_path / "u.cube")


def test_conversion_tablas_nombres_y_de(conv):
    tablas, nombres, de = conv
    assert [len(t) for t in tablas] == [P.TAM] * 3
    assert nombres == ["Fuji32", "Pelicula17", "TealOrangeL"]   # alfabético, truncado a 11
    print("ΔE 32³, 17³ y 33³ (medio, p95):", de)
    assert de[0][0] < 1.5 and de[1][0] < 1.5 and de[2][0] < 1.0


def test_relleno_con_identidad(tmp_path):
    C.escribe_cube(tmp_path / "a.cube", C.SINT["identidad"], 17, "t")
    tablas, nombres, de = S.convierte(S.lee_cubes(tmp_path))
    assert nombres == ["a", "Neutro", "Neutro"] and de[1:] == [(0.0, 0.0)] * 2
    assert tablas[1] == C.empaqueta_hw(C.descompone(C.SINT["identidad"], False, False, True).q, C.BIN.read_bytes())


def test_mas_de_tres_cube_falla(tmp_path):
    for i in range(4):
        C.escribe_cube(tmp_path / f"{i}.cube", C.SINT["identidad"], 17, "t")
    with pytest.raises(ValueError):
        S.lee_cubes(tmp_path)


def test_nombres_en_la_opcion_lut(conv):
    aj = S.ajustes_con_nombres(conv[1])
    lut = next(a for a in aj if a.id == "lut")
    assert [t for t, _ in lut.opciones] == ["Off", "Fuji32", "Pelicula17", "TealOrangeL"]
    assert [v for _, v in lut.opciones] == [0, 1, 2, 3]
    assert [a.id for a in aj] == [a.id for a in cfw_ajustes.AJUSTES]
    assert next(a for a in cfw_ajustes.AJUSTES if a.id == "lut").opciones[1][0] == "Teal&Orange"   # no muta lo de fábrica
    assert cfw_ajustes.configurar_menu(aj).SETTINGS["lut"] is not None


def test_seleccion_1_a_3_entrega_la_tabla_y_off_la_de_fabrica(conv):
    img = P.apply_bytes(C.BIN.read_bytes(), conv[0])
    for opcion in (1, 2, 3):
        P.emular(img, 0, opcion)
        assert P.emular.mem == conv[0][opcion - 1]
    assert P.emular(img, 0, 0, orig=0x11223344) == 0x11223344 and P.emular(img, 1, 9, orig=0x55) == 0x55
    # cada gancho (SA y MOV) entrega la misma tabla
    P.emular(img, 1, 2)
    assert P.emular.mem == conv[0][1]


def test_parche_por_defecto_sin_cambios(conv):
    base = C.BIN.read_bytes()
    assert P.apply_bytes(base) == P.apply_bytes(base, P.tablas_por_defecto())
    assert P.apply_bytes(base, conv[0]) != P.apply_bytes(base)
