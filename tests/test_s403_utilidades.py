"""Utilidades de s403 sin prueba propia: memscan, dual_scan y e10_vtable_refs (datos)."""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "analysis/s403_pendientes"
sys.path.insert(0, str(BASE))
import dual_scan
import memscan


def test_memscan_finds_wide_ldr_with_displacement():
    blob = bytes.fromhex("d1f8a406") + bytes.fromhex("7047")  # ldr.w r0,[r1,#0x6a4]; bx lr
    hits = memscan.mem_accesses(blob, {0x6A4})
    assert len(hits) == 1 and hits[0][1].startswith("ldr")
    assert memscan.mem_accesses(blob, {0x6A8}) == []


def test_dual_scan_index_groups_references_by_target():
    refs = [{"target": 1, "ldr": 10}, {"target": 2, "ldr": 20}, {"target": 1, "ldr": 30}]
    assert [r["ldr"] for r in dual_scan.index(refs)[1]] == [10, 30]


def test_dual_scan_hexify_only_converts_large_integers():
    assert dual_scan.hexify({"a": 0x43541000, "b": [5, 0x1000]}) == {"a": "0x43541000", "b": [5, "0x1000"]}


def test_e10_vtable_refs_every_reference_has_owner():
    d = json.loads((BASE / "e10_vtable_refs.json").read_text())
    assert d["clases_con_constructor"] == len(d["refs"]) <= d["vtables"]
    assert all("propietario" in r for refs in d["refs"].values() for r in refs)
