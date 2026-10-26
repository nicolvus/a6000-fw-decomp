"""D1: etiquetas del censo cuyo emisor cuelga (llamadas directas) de las raíces de captura; contra d1_alcance*.json."""
import json
from pathlib import Path

DIR = Path(__file__).resolve().parents[1] / "analysis/s403_pendientes"
LOOSE = json.loads((DIR / "d1_alcance.json").read_text())
STRICT = json.loads((DIR / "d1_alcance_estricto.json").read_text())
E8 = json.loads((DIR / "e8_alcance.json").read_text())
PRIORIDAD_1 = {"[SDF_ERR]", "[CMDMLTSYNC]", "[SYNCENCSTART]", "[SYNCSETMODE]", "[EVF]", "[PANELEVF]", "[PNLEVF]", "[VSYNC]"}


def reached(data: dict) -> set[str]:
    return {e["etiqueta"] for e in data["etiquetas"] if e["alcanzadas"]}


def test_graph_reproduces_rea_reach_of_e8():
    mine = {s for s, (_, depth) in LOOSE["calibracion_e8"].items() if depth is not None}
    assert mine == {s for s, v in E8.items() if v["raices"]}


def test_only_ten_of_226_labels_have_an_emitter_under_capture_roots():
    assert len(LOOSE["etiquetas"]) == 226
    assert reached(LOOSE) == reached(STRICT) == {
        "[EXL]", "[LGA]", "[CID]", "[FILE_NUM]", "[FSYSMODE]", "[SIZE]", "[STAT]", "[IN1]", "[IN2]", "[MODE_SNR_BUS_THROUGH]"}


def test_priority_one_labels_are_not_reached():
    assert not PRIORIDAD_1 & reached(LOOSE)
