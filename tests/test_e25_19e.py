"""E25-19e: origen de cap+0x74f y selector 3/4 del controlador VD, ejecutados contra av-cam.bin."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e25_19e"))
import campos_g
import cubren_74f
import plan142
import selector_vd
from desmontar import BIN

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="av-cam.bin no disponible")


def test_w1_copia_plan_13f_142_a_cap_74c_74f_y_142_es_par():
    assert {(c["plan"], c["cap"]) for c in plan142.copia_w1()} >= {("0x13f", "0x74c"), ("0x140", "0x74d"), ("0x141", "0x74e"), ("0x142", "0x74f")}
    r = plan142.ramas()
    assert len(r) == 8 and all(x["par"] for x in r)  # 2×lookup: W1 nunca copia un 1


def test_hay_ocho_stores_que_cubren_74f_o_74c_74e():
    a = {x["addr"] for x in cubren_74f.cubren(BIN.read_bytes())}
    assert {0x4354AF88, 0x4354B0AC, 0x4354C868} <= a and len(a) == 11


def test_g_60_7e_7f_sin_escritor_distinto_de_clear():
    e = [x for x in campos_g.accesos(BIN.read_bytes()) if x["tipo"] == "W" and x["campo"] in ("0x7e", "0x7f")]
    assert [x["addr"] for x in e] == ["0x438c2724"]  # único store: limpia G+0x7e tras gestionar la cancelación


def test_selector_3_y_4_difieren_en_208_y_258():
    d = BIN.read_bytes()
    t = selector_vd.tabla(d)
    assert t == {1: 0x436C75D2, 2: 0x436C7672, 3: 0x436C76E0, 4: 0x436C770A}
    s3, s4 = selector_vd.bloque(3, t[4], d), selector_vd.bloque(4, 0x436C7744, d)
    i3, i4 = next(i for i, x in enumerate(s3) if "#0x43ad2bbc" in x), next(i for i, x in enumerate(s4) if "#0x43ad2bbc" in x)
    assert s3[i3 - 1].endswith("movs r1, #1") and s4[i4 - 1].endswith("movs r1, #0")  # +0x208 bit0
    assert s3[-2].endswith("movs r1, #0") and s4[-1].endswith("movs r7, #0")  # +0x258 = 0 / 1 y r7 solo en 4


def test_lecturas_fisicas_74f_constante_74d_cae_al_final():
    for f in (ROOT / "analysis/e25-19e").glob("lectura-4s-*.json"):
        m = json.loads(f.read_text())["muestras"]
        v = [bytes.fromhex(x["0x740"])[0xC:0x10].hex() for x in m]
        assert set(v) <= {"00010001", "00000001"} and v[-1] == "00000001" and all(x[6:] == "01" for x in v)
