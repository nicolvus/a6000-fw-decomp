"""E17: listas de topología no resueltas por E10; contra e17_listas.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e17_listas.json").read_text())
RESOLVED = {"pila", "heap", "miembro_proyectado", "estatica", "nula"}


def flat(lst: list) -> set[str]:
    return {y for x in lst for y in (x if isinstance(x, list) else [x])}


def test_resolution_coverage_is_declared():
    assert DATA["no_resueltos_e10"] == 151
    assert sum(e["motivo"] in RESOLVED for e in DATA["sitios"]) == 72  # el resto queda sin resolver (E17)


def test_shooting_models_are_fully_resolved_without_yc_rows():
    shooting = DATA["modelos_de_disparo"]
    assert sum(v["sitios"] for v in shooting.values()) == 20
    assert all(v["sitios"] == v["resueltos"] and v["filas_yc"] == 0 for v in shooting.values())


def test_row_b4_is_created_only_by_scalar_pb():
    classes = set()
    for e in DATA["sitios"]:
        lists = [e["lista"]] if "lista" in e else [o["lista"] for o in e.get("origenes", []) if isinstance(o["lista"], list)]
        if any("0xb4" in flat(lst) for lst in lists):
            classes.add(e["clase"])
    assert classes == {"ModelScalarPb"}
