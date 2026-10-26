"""E8: lectores del objeto 0x43f72d02 que cuelgan de las raíces de captura; contra e8_alcance.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e8_alcance.json").read_text())


def test_half_of_readers_hang_from_capture_roots():
    assert len(DATA) == 14
    on_path = [s for s, v in DATA.items() if v["raices"]]
    assert on_path == ["0x438363e4", "0x43857f8a", "0x43857faa", "0x43858130", "0x438581a4", "0x4385971a", "0x4385994e"]
    assert DATA["0x4385994e"]["raices"] == ["0x438c7800", "0x438c828c"]  # llamadores de SetExposure, no el origen del bloque B


def test_unresolved_and_isolated_readers():
    assert DATA["0x438e7088"]["proc"] is None  # rutina sembrada a mano: REA no la ubica
    assert DATA["0x43861404"]["raices"] == []  # lector 1 de S176
