"""Las trazas publicadas deben coincidir con bytes reales, no solo con otro JSON."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REPORTS = sorted(ROOT.glob("analysis/s6*/*.json"))
FIRMWARE = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"


@pytest.fixture(scope="module")
def firmware() -> bytes:
    return FIRMWARE.read_bytes()


@pytest.mark.parametrize("path", REPORTS, ids=lambda p: p.parent.name)
def test_trace_addresses_and_prefix_lengths(path: Path, firmware: bytes) -> None:
    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict) or "trace_strings" not in report:
        pytest.skip("Otro esquema; fuera del alcance de esta comprobación")
    for trace in report["trace_strings"]:
        offset = int(trace["vaddr"], 16) - 0x43541000
        text = trace["text"].encode()
        assert 0 <= offset < len(firmware)
        assert firmware[offset:offset + len(text)] == text, trace
    if "prefix_length" in report:
        assert report["prefix_length"] == len(report["prefix"])
    if "prefix_lengths" in report:
        assert report["prefix_lengths"] == [len(p) for p in report["prefixes"]]
