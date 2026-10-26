"""E4: `0x4379d378` = IsNeedForceS1ON(trig); contra e4_trig.json."""
import json
from pathlib import Path

D = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e4_trig.json").read_text())


def test_function_is_is_need_force_s1on():
    assert D["cadena_de_error"]["texto"].endswith("strange trig in IsNeedForceS1ON : %d")
    assert D["limite_trig"] == "r1, #0xa"
    assert set(D["llamadores"].values()) == {"ldr r1, [r5, #0x10]"}  # el trig es el campo +0x10 del registro REL_EVT


def test_trig_classification():
    c = D["clasificacion"]
    assert [t for t, v in c.items() if v == "forzar_S1"] == ["3", "8", "9", "10"]
    assert [t for t, v in c.items() if v == "condicional"] == ["2"]
    assert [t for t, v in c.items() if v == "no_forzar"] == ["0", "1", "4", "5", "6", "7"]
    assert D["tabla_43ca530e"]["llamadores"] == {"0x4379e13e": "mov r1, r8"}  # indexada por 0x43aea264, no por el trig
