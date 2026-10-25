"""Contrato del escritor S[0], incluido el argumento Thumb pasado por pila."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s205_staging", ROOT / "analysis/s205_imager_s0_writer/verify_staging.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_staging_writes_actual_s_from_mode_context():
    result = MODULE.audit(MODULE.BINARY.read_bytes())
    assert result["state"] == "0x43eb35d0"
    assert result["state_slot"] == "0x44020c9c"
    assert result["selector_store"] == "0x43843a5e"
    assert result["source"] == "u8(*(ctx + 0x20) + 1)"
    assert result["rows"] == {"source": "0x43eb07fc", "count": 4, "size": 16,
                              "source_offset": "0x2c", "destination_offset": "0x64",
                              "condition": "selector == 3"}
    assert result["electronic_end_of_integration"] == "NO_VERIFICADO"


@pytest.mark.parametrize("address", [0x44020C9C, 0x437B61B4, 0x43843A5E, 0x43843ADA])
def test_wrong_pointer_stack_argument_or_gate_is_rejected(address):
    data = bytearray(MODULE.BINARY.read_bytes())
    data[address - MODULE.BASE] ^= 4
    with pytest.raises(AssertionError):
        MODULE.audit(bytes(data))
