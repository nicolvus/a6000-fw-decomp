"""E14: los 14 escritores de `+0x654` no guardan nunca una constante 2 o 3; contra e14_writers.json."""
import json
from collections import Counter
from pathlib import Path

ROWS = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e14_writers.json").read_text())


def test_fourteen_writers_classified():
    assert len(ROWS) == 14
    assert Counter(r["clase"] for r in ROWS) == {"bloque_de_parametros": 10, "estado_fsm": 4}


def test_no_writer_stores_constant_two_or_three():
    consts = {r["addr"]: r["definicion"] for r in ROWS if r["origen"] in ("constante", "constante_0")}
    assert [a for a in consts] == ["0x4364c27e", "0x438691ba", "0x43a471ec", "0x43b0b8ac"]
    assert consts["0x438691ba"].endswith("movs r3, #0") and consts["0x43a471ec"].endswith("movs r1, #6")  # 0 en el bloque; 6 en la FSM


def test_block_values_come_from_data():
    block = Counter(r["origen"] for r in ROWS if r["clase"] == "bloque_de_parametros")
    assert block["copia_de_otro_bloque"] == 3 and block["pila"] == 2
