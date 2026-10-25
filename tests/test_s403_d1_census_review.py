"""Coherencia de la revisión léxico-estructural del censo (D1)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = json.loads((ROOT / "analysis/s403_pendientes/d1_census_review.json").read_text())
CENSUS = json.loads((ROOT / "analysis/s178_census/pendientes_auditados.json").read_text())


def test_covers_every_pending_label_once():
    pending = {e["etiqueta"] for e in CENSUS["etiquetas"] if e["estado_censo"] == "pendiente"}
    reviewed = [r["etiqueta"] for r in REVIEW["etiquetas"]]
    assert len(reviewed) == len(set(reviewed)) == 226
    assert set(reviewed) == pending


def test_summary_matches_rows():
    rows = REVIEW["etiquetas"]
    res = REVIEW["resumen"]
    assert res["total"] == len(rows)
    assert sum(res["por_clase"].values()) == len(rows)
    assert res["por_clase"] == {"modulo_propio": 101, "subetiqueta": 118, "mixto": 1, "campo_de_formato": 6}


def test_census_verdicts_untouched():
    verdicts = {r["etiqueta"]: r["veredicto_censo"] for r in REVIEW["etiquetas"]}
    assert sorted(t for t, v in verdicts.items() if v == "ACEPTO") == ["[DECMODEMGR]", "[EXL]", "[IMAGING_IMG]", "[SFR]"]
    assert list(verdicts.values()).count("NO_VERIFICADO") == 222
