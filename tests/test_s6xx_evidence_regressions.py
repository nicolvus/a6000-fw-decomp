"""Regresiones: evidencia real, cobertura no vacía y estados prudentes."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
FW = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/"
      "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
MODULES = {
    int(p.parent.name[1:4]): json.loads(p.read_text())
    for p in (ROOT / "analysis").glob("s6[0-2][0-9]_*/*.json")
    if 605 <= int(p.parent.name[1:4]) <= 627
}


def test_complete_inventory():
    assert set(MODULES) == set(range(605, 628))
    assert sum(len(j["trace_strings"]) for j in MODULES.values()) == 94


def test_exact_bytes_include_whitespace_and_terminator():
    for j in MODULES.values():
        for t in j["trace_strings"]:
            off = int(t["vaddr"], 16) - BASE
            expected = t["text"].encode("ascii") + b"\0"
            assert off >= 0
            assert FW[off:off + len(expected)] == expected, t["vaddr"]


def test_twin_addresses_and_deltas():
    twins = MODULES[606]["trace_strings"]
    assert len(twins) == 7
    for t in twins:
        off = int(t["twin_vaddr"], 16) - BASE
        expected = t["twin_text"].encode("ascii") + b"\0"
        assert FW[off:off + len(expected)] == expected, t["twin_vaddr"]
        assert int(t["twin_vaddr"], 16) - int(t["vaddr"], 16) == t["delta"]


def test_prefix_lengths_are_byte_lengths():
    for j in MODULES.values():
        for name in ("prefix", "twin_prefix", "core_prefix"):
            if name in j:
                assert j[name + "_length"] == len(j[name].encode("ascii"))
        if "composite_prefix_length" in j:
            assert j["composite_prefix_length"] == len(
                (j["prefix"] + j["core_prefix"]).encode("ascii")
            )
        if "prefix_lengths" in j:
            assert j["prefix_lengths"] == [len(p.encode("ascii")) for p in j["prefixes"]]


def test_no_functional_negative_from_keywords():
    for j in MODULES.values():
        status = j["verification_status"]["linea_obturador"]
        assert status["status"] == "NO_VERIFICADO"
        assert status["verified"] is False


def test_no_positive_logger_claim_without_instructions():
    for session, j in MODULES.items():
        status = j["verification_status"]["logger_dual"]
        if session in {607, 611, 616}:
            assert j["logger_dual"] is True
            assert status["verified"] is True
            assert status["global_logger_verified"] is True
        else:
            assert j.get("logger_dual") is None
            assert status["verified"] is False
            assert status["global_logger_verified"] is False


def test_alternative_evidence_has_explicit_coverage():
    for j in MODULES.values():
        status = j["verification_status"]
        assert status["differential"]["status"] == "NO_VERIFICADO"
        assert status["metadata"]["verified"] is True
    assert MODULES[606]["verification_status"]["twin_strings"]["count_ok"] == 7
    for session in (608, 611, 616):
        assert MODULES[session]["verification_status"]["core_strings"]["verified"] is True


def test_empty_alias_is_not_verified_evidence():
    status = MODULES[618]["verification_status"]
    assert status["trace_strings"]["verified"] is False
    assert status["linea_obturador"]["verified"] is False
