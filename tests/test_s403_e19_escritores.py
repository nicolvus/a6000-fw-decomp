"""E19: escritores del campo +0x6a4 (id DFE de `[LGA]`); contra e19_escritores.json y e18_dfe_param.json."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "analysis/s403_pendientes"
DATA = json.loads((BASE / "e19_escritores.json").read_text())
DFE = {r["id"]: r for r in json.loads((BASE / "e18_dfe_param.json").read_text())["ids"]}


def test_ten_32bit_writers_seven_in_mode_block():
    assert len(DATA["escritores"]) == 10
    assert sum(r["clase"].startswith("bloque") for r in DATA["escritores"]) == 7


def test_mode_block_always_stores_immediate_one():
    assert DATA["valores_bloque_de_modo"] == [1]
    assert all(r["fuente"].get("inmediato") == 1 for r in DATA["escritores"] if r["clase"].startswith("bloque"))


def test_id_one_resolves_to_static_record_574():
    assert (DFE[1]["registro"], DFE[1]["suma"]) == ("0x43bb9264", 574)
