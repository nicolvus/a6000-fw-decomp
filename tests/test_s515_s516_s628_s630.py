"""Pruebas de S515, S516, S628, S629 y S630 (cadenas y referencias PIC de av-cam A6000)."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis/s515_s516_s628_s630_modulos/modulos.json"
BIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
MODS = json.loads(DATA.read_text())["modules"]
COUNTS = {"S515": 154, "S516": 41, "S628": 1, "S629": 1, "S630": 1}


@pytest.mark.parametrize("sid,n", COUNTS.items())
def test_string_counts(sid, n):
    m = MODS[sid]
    assert m["counts"]["a6000_fw321"] == n == len(m["a6000_strings"])
    assert all(m["tag"] in s["text"] for s in m["a6000_strings"])


def test_differential_counts():
    assert MODS["S515"]["counts"] == {"a6000_fw321": 154, "a7s_fw320": 75, "a6300_fw201": 96}
    for sid in ("S628", "S629", "S630"):
        assert MODS[sid]["counts"]["a7s_fw320"] == MODS[sid]["counts"]["a6300_fw201"] == 0


def test_every_pnl_and_single_trace_has_pic_ref():
    assert MODS["S516"]["with_pic_ref"] == 41
    for sid in ("S628", "S629", "S630"):
        assert MODS[sid]["with_pic_ref"] == 1


@pytest.mark.skipif(not BIN.exists(), reason="firmware no presente")
def test_strings_match_bytes_exactly():
    blob = BIN.read_bytes()
    for m in MODS.values():
        for s in m["a6000_strings"]:
            off = int(s["vaddr"], 16) - BASE
            assert blob[off:off + len(s["text"].encode("latin1")) + 1] == s["text"].encode("latin1") + b"\0"
