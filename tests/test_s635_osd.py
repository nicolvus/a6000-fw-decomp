"""S635: la etiqueta [OSD] (A6000 fw3.21)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s635_osd"))
import verify_osd as V

D = V.build()


def test_osd_una_cadena_una_funcion_sin_referencias():
    assert (D["cadenas"], D["sitios"], D["ejemplo"]) == (1, 1, "[VDF][OSD] VDF_EVF_OUT_MODE_ON_LR_THROUGH")
    assert [f["func"] for f in D["funciones"]] == ["0x4368e31a"] and D["obturador"] == []
    assert not any(D["referencias_funcion"].values())
    assert D["tokens"] == {"a6000_fw321": 1, "a7s_fw320": 1, "a6300_fw201": 0}


def test_json_versionado_coincide():
    assert json.loads((ROOT / "analysis/s635_osd/osd.json").read_text()) == json.loads(json.dumps(D))
