"""Verifica integridad y evidencia estática S40 sin ejecutar firmware."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    findings = json.loads((OUT / "s40-findings.json").read_text())
    assert hashlib.sha256((ROOT / findings["binary"]).read_bytes()).hexdigest() == SHA
    for name in findings["exports"]:
        data = json.loads((OUT / name).read_text())
        assert data["sha256"] == SHA
        assert all(row.get("completed") or row.get("status") == "listing_only_no_function"
                   for row in data["functions"])
        assert (OUT / name.replace(".json", ".c")).exists()
    writers = json.loads((OUT / "s40-writers.json").read_text())
    copy = next(row for row in writers["functions"] if row.get("entry") == "43804c5c")
    assert "43804cd4 mov.w r2,#0x560" in copy["listing"]
    assert "43804cdc blx 0x439c5320" in copy["listing"]
    tables = json.loads((OUT / "s40-tables.json").read_text())
    assert tables["dispatch_base"] == "43fff30c"
    assert tables["selector_base"] == "43ca3c21"
    assert tables["selector_raw"] == "01010001"
    handlers = {row["command"]: row["handler"] for row in tables["dispatch"]}
    assert handlers[0x4000] == "43804059"
    assert handlers[0x4036] == "4380394d"
    api = json.loads((OUT / "s40-api.json").read_text())
    fields = {row["address"]: row["references"] for row in api["data_queries"]}
    assert len(fields["43edf6a8"]) == 2
    assert any("43803958" in ref and "WRITE" in ref for ref in fields["43edf6cc"])
    source = json.loads((OUT / "s40-source.json").read_text())
    handler = next(row for row in source["functions"] if row.get("entry") == "43809148")
    assert "case 0x3023:" in handler["pseudo_code"]
    assert "43809374 ldrb r3,[r4,#0xe]" in handler["listing"]
    assert "43809378 str.w r3,[r0,#0x458]" in handler["listing"]
    assert findings["coverage"] == "PARCIAL"
    for name in ["s38-project-before.sha256", "s38-rep-before.sha256"]:
        for line in (OUT / name).read_text().splitlines():
            digest, filename = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest
    print("S40 audit PASS: firmware/proyecto intactos; exports y copia 0x560 verificados")


if __name__ == "__main__":
    main()
