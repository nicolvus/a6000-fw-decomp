"""Reconstrucción de S176: procedencia PIC y ceros condicionales reales."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s176_readers", ROOT / "analysis/s176_imager_state_readers/readers_audit.py",
)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


@pytest.fixture(scope="module")
def image():
    return AUDIT.BINARY.read_bytes()


def test_both_readers_resolve_same_state_from_original_bytes(image):
    result = AUDIT.audit(image)
    assert result["got_base"] == "0x4401eee4"
    assert result["got_slot"] == "0x4401f990"
    assert result["state"] == "0x43f72d02"
    assert result["single_read"] == {"site": "0x43861410", "offset": "0xac"}
    assert result["physical_semantics"] == "NO_VERIFICADO"


def test_zero_overrides_cover_eight_destination_words(image):
    rows = AUDIT.audit(image)["zero_overrides"]
    assert [row["state_offset"] for row in rows] == [hex(v) for v in range(0x30, 0x38)]
    assert [row["destination_offset"] for row in rows] == [
        "0x664", "0x66c", "0x674", "0x67c", "0x684", "0x68c", "0x690", "0x694",
    ]
    assert all(row["value"] == 0 and row["condition"] == "state_byte == 0" for row in rows)


def test_default_six_belongs_to_first_reader_tail(image):
    default = AUDIT.audit(image)["first_reader_default"]
    assert default["input_offset"] == "0xac"
    assert default["zero_replacement"] == 6
    assert default["instruction"] == "0x438fec74"


@pytest.mark.parametrize("address", [0x43861420, 0x438694C8, 0x438693F2, 0x438FEC74])
def test_changed_pool_or_branch_cannot_certify_old_claim(image, address):
    changed = bytearray(image)
    changed[address - AUDIT.BASE] ^= 4
    with pytest.raises(AssertionError):
        AUDIT.audit(bytes(changed))
