"""Contrasta evidencia estática S34 y preservación del proyecto, sin firmware."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    spec = importlib.util.spec_from_file_location("s32_audit", OUT / "s32-audit.py")
    assert spec is not None and spec.loader is not None
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    blob = previous.BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == EXPECTED
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in [OUT / "silent-liro.gpr", *sorted((OUT / "silent-liro.rep").rglob("*"))]
              if p.is_file() and not p.name.endswith(".lock")}
    manifest = OUT / "s34-integrity.json"
    if "--baseline" in sys.argv:
        assert not manifest.exists(), "No sobrescribir baseline S34"
        manifest.write_text(json.dumps({"source_sha256": EXPECTED,
                                       "project_hashes": hashes}, indent=2) + "\n")
        print("PASS: SHA y baseline S34 capturado antes de abrir Ghidra")
        return
    assert hashes == json.loads(manifest.read_text())["project_hashes"]
    initial = json.loads((OUT / "s34-timing.json").read_text())
    assert initial["source_sha256"] == EXPECTED
    rows = []
    for path in sorted(OUT.glob("s34-*.json")):
        data = json.loads(path.read_text())
        if "functions" in data:
            assert data["source_sha256"] == EXPECTED
            rows.extend(data["functions"])
    for row in rows:
        if not row["query"].startswith("@") and "entry" in row:
            assert row["status"] == "decompiled" and not row["error"], row["query"]
    calls = previous.branches(blob, {0x43814EA0})
    assert {c["site"] for c in calls} == {"4355164a", "435536be", "435557de"}
    assert not previous.branches(blob, {0x435503B0, 0x435525C0, 0x43554590})
    recovered = {c["site"] for f in rows for c in f.get("calls_and_jumps", [])
                 if c["target"] == "43814ea0"}
    assert recovered == {c["site"] for c in calls}
    functions = {f["entry"]: f for f in rows if "entry" in f}
    assert not previous.pic_candidates(blob, {0x43814EA0, 0x43814EA1})
    assert all(value.to_bytes(4, "little") not in blob
               for value in (0x43814EA0, 0x43814EA1))
    for slot, target in ((0x44020064, 0x435503B1), (0x44020E70, 0x435525C1),
                         (0x44021A2C, 0x43554591)):
        assert struct.unpack_from("<I", blob, slot - previous.BASE)[0] == target
    expected_edges = {
        "43814ea0": {("43815054", "436be554"), ("43815082", "436bdbfc")},
        "436bdbfc": {("436bddf8", "436c0354"), ("436bde20", "436c041c"),
                     ("436bde48", "436c04e4"), ("436bde60", "436c06fc"),
                     ("436be3a4", "43acb2e8")},
        "4379155c": {("437916d4", "43796954"), ("437917a4", "43560da8")},
        "4379210c": {("43792474", "43560de0"), ("43792510", "439018b0")},
        "437965ec": {("43796690", "4381bf38")},
    }
    for entry, expected in expected_edges.items():
        actual = {(c["site"], c["target"])
                  for c in functions[entry]["calls_and_jumps"]}
        assert expected <= actual, entry
    converter = functions["43ad68e0"]["pseudo_code"]
    for constant in ("0x80000", "0x100000", "0x1000000", "0x2000000"):
        assert constant in converter
    assert "DAT_43e7ec28" in functions["436cfae0"]["pseudo_code"]
    assert "0x3380000" in functions["436cf954"]["pseudo_code"]
    assert "FUN_43560da8(0x1a,0x80)" in functions["43ae8d3e"]["pseudo_code"]
    assert "DAT_f3850500" in functions["436c019c"]["pseudo_code"]
    findings = json.loads((OUT / "s34-findings.json").read_text())
    report = {"result": "PASS", "source_sha256": EXPECTED,
              "project_unchanged": True, "direct_helper_calls": calls,
              "exported_queries": len(rows), "findings": findings["summary"],
              "unresolved_or_exploratory": findings["exploratory_limits"],
              "scope": findings["scope"]}
    (OUT / "s34-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: SHA, proyecto idéntico, tres llamadores, {len(rows)} consultas")
    print("| Estado | Hallazgo |")
    print("|---|---|")
    for row in findings["summary"]:
        print(f"| {row['status']} | {row['finding']} |")


if __name__ == "__main__":
    main()
