"""S634: etiquetas de OTROS (A6000 fw3.21)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/camera_closure"))
import labels as L

SAVED = json.loads((ROOT / "analysis/s634_otros/otros.json").read_text())


def test_inventario_completo_y_sin_obturador():
    assert len(SAVED) == 146 and all(v["estado_previo"] == "pendiente" for v in SAVED.values())
    assert not any(v["obturador"] for v in SAVED.values())


def test_muestra_reproducible():
    for k in ("[DECMODEMGR]", "[NG]"):
        got = L.evaluate(k); want = SAVED[k]
        assert {x: got[x] for x in ("cadenas", "sin_sitio", "sitios", "tokens", "fuentes")} == {x: want[x] for x in ("cadenas", "sin_sitio", "sitios", "tokens", "fuentes")}
        assert [f["func"] for f in got["funciones"]] == [f["func"] for f in want["funciones"]]
