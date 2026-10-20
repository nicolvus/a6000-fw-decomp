"""Contrasta evidencia S41 e integridad sin ejecutar firmware."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    findings = json.loads((OUT / "s41-findings.json").read_text())
    assert hashlib.sha256((ROOT / findings["binary"]).read_bytes()).hexdigest() == SHA
    for filename in findings["exports"]:
        data = json.loads((OUT / filename).read_text())
        assert data["sha256"] == SHA
        for row in data["functions"]:
            assert row.get("completed") or row.get("status") == "listing_only_no_function"
        assert (OUT / filename.replace(".json", ".c")).exists()
    data = json.loads((OUT / "s41-send.json").read_text())
    raw = {row["query"]: row["raw64"] for row in data["functions"]}
    assert int.from_bytes(bytes.fromhex(raw["437feedc"][:8]), "little") == 0x30001
    assert int.from_bytes(bytes.fromhex(raw["43806e64"][:8]), "little") == 0x3030F
    entry = json.loads((OUT / "s41-entry.json").read_text())
    functions = {row.get("entry"): row for row in entry["functions"]}
    assert "param_1 + -4" in functions["43b0091c"]["pseudo_code"]
    assert "FUN_4356120c(param_3,uStack_14)" in functions["437feef8"]["pseudo_code"]
    enums = json.loads((OUT / "s41-enums.json").read_text())
    raw_enums = {row["query"]: bytes.fromhex(row["raw64"]) for row in enums["functions"]}
    assert [int.from_bytes(raw_enums["43bc59e0"][i:i + 4], "little")
            for i in range(0, 12, 4)] == [1, 0, 5]
    assert [int.from_bytes(raw_enums["43bc5a50"][i:i + 4], "little")
            for i in range(0, 16, 4)] == [1, 2, 0, 3]
    thumb = json.loads((OUT / "s41-3023-thumb.json").read_text())
    for row in thumb["functions"][:4]:
        assert not row.get("pseudo_disassembly_error")
        assert row["temporary_thumb_listing"][0].endswith("ldr r0,[0x" +
                                                            format(int(row["query"], 16) + 8, "x") + "]")
        assert row["temporary_thumb_listing"][-1].endswith("bx lr")
    assert findings["coverage"] == "PARCIAL"
    assert findings["physical_capture"] == "NO_VERIFICADO"
    shutter = json.loads((OUT / "s41-shutter-conditions.json").read_text())
    shutter_functions = {row["query"]: row for row in shutter["functions"]}
    assert "43845f30 ldr.w r2,[r3,#0x210]" in shutter_functions["43844e80"]["listing"]
    assert "43845f34 str.w r2,[r4,#0x41c]" in shutter_functions["43844e80"]["listing"]
    assert "438c830c bl 0x436d6320" in shutter_functions["438c828c"]["listing"]
    assert "436d6fb6 ldrb.w r9,[r1,#0x9]" in shutter_functions["436d6f6c"]["listing"]
    for filename in ("s38-project-before.sha256", "s38-rep-before.sha256"):
        for line in (OUT / filename).read_text().splitlines():
            digest, path = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    print("S41 audit PASS: SHA/proyecto, colas y exports; sin ejecución de firmware")


if __name__ == "__main__":
    main()
