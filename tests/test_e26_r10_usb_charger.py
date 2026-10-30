"""Unit tests for E26-R10 USB Charger descriptor validation."""

import importlib.util
import sys
from pathlib import Path

# Locate the repo root from this test file, then the analysis module.
_repo_root = Path(__file__).resolve().parent.parent
_analysis_dir = _repo_root / "analysis" / "e26-recovery"
if str(_analysis_dir) not in sys.path:
    sys.path.insert(0, str(_analysis_dir))

_spec = importlib.util.spec_from_file_location(
    "r10_usb_descriptor_parse", _analysis_dir / "r10-usb-descriptor-parse.py"
)
assert _spec is not None and _spec.loader is not None
_r10 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r10)
find_vidpid = _r10.find_vidpid
parse_descriptors = _r10.parse_descriptors
verify = _r10.verify

DARWIN_CORE = _repo_root / "firmware" / "extracted" / "fw321" / "firmware.tar_unpacked" / "0640_darwin" / "darwin_core.bin"


def test_vidpid_found():
    data = DARWIN_CORE.read_bytes()
    pos = find_vidpid(data)
    assert pos >= 0
    assert data[pos : pos + 4] == b"\x4c\x05\x94\x09"


def test_descriptor_walk():
    data = DARWIN_CORE.read_bytes()
    pos = find_vidpid(data)
    descs = parse_descriptors(data, pos - 8)
    types_found = {d["bType"] for d in descs}
    assert 0x01 in types_found  # Device
    assert 0x02 in types_found  # Configuration
    assert 0x04 in types_found  # Interface
    assert 0x21 in types_found  # HID
    assert 0x05 in types_found  # Endpoint
    assert 0x03 in types_found  # String


def test_fields_match_observed():
    data = DARWIN_CORE.read_bytes()
    pos = find_vidpid(data)
    descs = parse_descriptors(data, pos - 8)
    result = verify(descs)
    assert result["failures"] == [], result["failures"]
    assert "Sony" in result["strings"]
    assert "USB Charger" in result["strings"]
    # HID: only one report descriptor (Input), no Output/Feature declared.
    assert result["hid_num_descriptors"] == 1
    assert result["output_report_declared"] is False
    assert result["feature_report_declared"] is False


def test_descriptor_types_known():
    data = DARWIN_CORE.read_bytes()
    pos = find_vidpid(data)
    descs = parse_descriptors(data, pos - 8)
    # No vendor-specific or unknown descriptor types beyond standard USB/HID.
    known = {0x01, 0x02, 0x03, 0x04, 0x05, 0x21}
    for d in descs:
        assert d["bType"] in known, f"unknown descriptor type 0x{d['bType']:02x}"


if __name__ == "__main__":
    test_vidpid_found()
    test_descriptor_walk()
    test_fields_match_observed()
    test_descriptor_types_known()
    print("All E26-R10 USB Charger tests passed.")
