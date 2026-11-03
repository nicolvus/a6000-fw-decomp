"""S636: campos [D0]-[D7] de [CAM_UTIL_ADJ] (A6000 fw3.21)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s636_dfields"))
import verify_dfields as V

D = V.build()


def test_dos_trazas_una_funcion():
    assert [(c["vaddr"], c["sitios"], c["funciones"]) for c in D["cadenas"]] == [
        ("0x43ccde70", ["0x43900abc"], ["0x43900a24"]), ("0x43ccdeae", ["0x43900ae2"], ["0x43900a24"])]
    assert D["cadenas"][0]["refs_funcion"]["0x43900a24"]["literal"] == ["0x4401f7a4"]
    assert all(c["obturador"] == [] for c in D["cadenas"])
    assert all(v == {"a6000_fw321": 1, "a7s_fw320": 0, "a6300_fw201": 0} for v in D["tokens"].values()) and len(D["tokens"]) == 8


def test_json_versionado_coincide():
    assert json.loads((ROOT / "analysis/s636_dfields/dfields.json").read_text()) == json.loads(json.dumps(D))
