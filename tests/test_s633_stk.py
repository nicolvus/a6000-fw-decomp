"""S633: cadenas [TRK]: [STK…] y etiquetas [STK_*] (A6000 fw3.21)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s633_stk"))
import verify_stk as V

D = V.build()


def test_cadenas_funciones_y_tablas():
    assert (D["cadenas_trk_stk"], D["cadenas_stk"], D["sitios"]) == (85, 76, 154)
    assert D["sin_sitio"] == ["0x43cfc7ea"]
    assert [r["func"] for r in D["funciones"]] == ["0x43a35384", "0x43a353d0", "0x43a3541c", "0x43a355d0", "0x43a3574c", "0x43a3588e", "0x43a36156", "0x43a36a06"]
    assert {r["func"]: r["punteros"]["literal"] for r in D["funciones"] if r["punteros"]["literal"]} == {
        "0x43a3541c": ["0x4401b984"], "0x43a355d0": ["0x4401b988"], "0x43a3574c": ["0x4401b98c"]}


def test_stk_sim_y_modelos():
    assert {s["etiqueta"]: (len(s["cadenas"]), s["funcion"], s["a7s"], s["a6300"]) for s in D["stk_sim"]} == {
        "[STK_AUTO_SAL]": (3, ["0x43a3588e"], 3, 0), "[STK_COLOR_SIM]": (2, ["0x43a36156"], 2, 0), "[STK_C_SIM]": (1, ["0x43a36156"], 1, 0),
        "[STK_TOUCH_SIM]": (2, ["0x43a36a06"], 2, 0), "[STK_T_SIM]": (1, ["0x43a36a06"], 1, 0)}
    assert D["tokens_stk"] == {"a6000_fw321": 76, "a7s_fw320": 76, "a6300_fw201": 0}
    assert all(v == [] for v in D["alcance_obturador"].values())


def test_json_versionado_coincide():
    assert json.loads((ROOT / "analysis/s633_stk/stk.json").read_text()) == json.loads(json.dumps(D))
