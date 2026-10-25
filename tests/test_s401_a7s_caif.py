"""Productor A7S del bit Silent: argumento de salida, selector y excepción."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s401_caif", ROOT / "analysis/s401_a7s_caif/verify_caif.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_caif_bit_and_sensor_mode_share_capture_selector():
    result = MODULE.audit(MODULE.BINARY.read_bytes())
    assert result["constructor"] == "0x43862e24"
    assert result["caller"] == "0x4382822c"
    assert result["payload_store"] == "0x438632b4"
    assert result["capture_selector"] == "root+0x78c == (root+0x20)+0x76c"
    assert result["normal_bit_0x20_condition"] == "selector == 2"
    assert result["diagnostic_override"] == 1
    assert result["sensor_modes"] == ["0x4e", "0x4f"]
    assert result["physical_delivery"] == "NO_VERIFICADO"


@pytest.mark.parametrize("address", [0x43863298, 0x4386329A, 0x438632AC, 0x438632B4, 0x4382828C])
def test_changed_condition_bit_or_payload_argument_is_rejected(address):
    data = bytearray(MODULE.BINARY.read_bytes())
    data[address - MODULE.BASE] ^= 4
    with pytest.raises(AssertionError):
        MODULE.audit(bytes(data))
