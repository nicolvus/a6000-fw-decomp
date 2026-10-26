"""D6: rutinas homólogas A6000↔A7S no ubicadas por REA; contra d6_homologos.json."""
import json
from pathlib import Path

ROWS = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/d6_homologos.json").read_text())


def test_seven_traces_compared_and_none_equal():
    assert [r["ficha"] for r in ROWS] == ["S605", "S605", "S606", "S607", "S611", "S611", "S611"]
    assert all(r["mejor"] and not r["mejor"]["root_igual_salvo_lineas"] for r in ROWS)
    assert ROWS[0]["mejor"]["len"] == [97, 52] and ROWS[4]["mejor"]["len"] == [83, 47]
