"""G22-FUNCIONES — el inventario de funciones (`docs/gui/g22-funciones-identicas.md`) tiene que seguir siendo auditable.

Una fila por función de la cámara con su estado, su medida y su límite. Este test no mide la UI: comprueba que el
documento no se pudre — 16 filas numeradas, estados del vocabulario, y **todos** los enlaces relativos (informes y
evidencias) apuntan a ficheros que existen. Si alguien mueve o borra una evidencia, el test falla.
"""
from __future__ import annotations

import re
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs/gui/g22-funciones-identicas.md"
ESTADOS = {"IGUAL", "EMULADO", "PARCIAL", "NO"}


def filas() -> list[list[str]]:
    return [[c.strip() for c in ln.strip().strip("|").split("|")]
            for ln in DOC.read_text(encoding="utf-8").splitlines() if re.match(r"^\| \d+ \|", ln)]


def test_hay_una_fila_por_funcion_con_estado_del_vocabulario() -> None:
    f = filas()
    assert len(f) >= 16, f"faltan filas: {len(f)}"
    for celdas in f:
        assert celdas[1], celdas
        assert celdas[2] in ESTADOS, f"fila {celdas[0]} ({celdas[1]}): estado «{celdas[2]}» fuera del vocabulario"


def test_los_enlaces_del_inventario_existen() -> None:
    texto = DOC.read_text(encoding="utf-8")
    rotos = []
    for destino in re.findall(r"\]\(([^)#]+)", texto):
        if destino.startswith("http"):
            continue
        if not (DOC.parent / destino).resolve().exists():
            rotos.append(destino)
    assert not rotos, f"enlaces rotos en el inventario: {rotos}"


def test_las_filas_que_dicen_no_o_parcial_llevan_su_limite() -> None:
    """Una fila PARCIAL o NO sin límite escrito es una fila que engaña: la columna 6 tiene que decir algo."""
    for celdas in filas():
        if celdas[2] in ("PARCIAL", "NO"):
            assert len(celdas) >= 6 and celdas[5], f"fila {celdas[0]} ({celdas[1]}) sin límite"
