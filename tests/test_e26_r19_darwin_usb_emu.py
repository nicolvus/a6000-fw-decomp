"""E26-R19 — callback USB de clase/vendor de Darwin: respuesta por tipo de petición (emulación, offline)."""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "e26-recovery"))
pytest.importorskip("unicorn")
E26 = importlib.import_module("r19_darwin_usb_emu")
pytestmark = pytest.mark.skipif(not E26.BIN.exists(), reason="darwin_core.bin ausente")


def respuesta(caso):
    fin, eventos, periferico = E26.run(E26.CASES[caso])
    assert fin == "ret"
    return eventos, periferico


def test_vendor_siempre_detenido_sin_efectos():
    for caso in ("vendor OUT", "vendor IN"):
        assert respuesta(caso) == ([("stop", 0, 0)], [])


def test_solo_hid_estandar_y_clase_get_report_set_idle():
    assert respuesta("estándar GET_DESCRIPTOR informe HID (0x22)")[0][0][::2] == (
        "EP0_send",
        0x13,
    )
    assert respuesta("estándar GET_DESCRIPTOR dispositivo (0x01)")[0] == [
        ("stop", 0, 0)
    ]
    assert respuesta("clase GET_REPORT")[0][0][0] == "EP0_send"
    for caso in ("clase SET_REPORT", "clase GET_IDLE", "clase GET_PROTOCOL"):
        assert respuesta(caso)[0] == [("stop", 0, 0)]


def test_set_idle_solo_borra_un_bit_de_registro_usb():
    eventos, periferico = respuesta("clase SET_IDLE")
    assert eventos == [] and periferico == [("0x40042144", "0x0")]
