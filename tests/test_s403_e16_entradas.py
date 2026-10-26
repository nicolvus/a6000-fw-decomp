"""E16: entradas del grupo que lee CURTAINMODE; contra e16_entradas.json."""
import json
from pathlib import Path

D = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e16_entradas.json").read_text())


def test_group_has_only_pointer_entries():
    assert len(D["grupo"]) == 10 and D["nodos"] == 26 and not D["truncado"]
    assert {k: v["punteros"] for k, v in D["raices"].items()} == {
        "0x43b1ae2a": ["0x44021968"], "0x43b1aea2": ["0x44021000"], "0x43b1aeee": ["0x440222f0"],
        "0x43b1b22e": ["0x44020134"], "0x43b1bc24": ["0x440223a4"], "0x43b1ce6e": ["0x44023408"]}
