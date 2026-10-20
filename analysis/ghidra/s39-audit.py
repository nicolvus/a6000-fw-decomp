"""Audita evidencia S39; no ejecuta firmware ni escribe el proyecto."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    findings = json.loads((OUT / "s39-findings.json").read_text())
    blob = (ROOT / findings["binary"]).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == SHA
    def word(address: int) -> int:
        return int(struct.unpack_from("<I", blob, address - 0x43541000)[0])
    assert word(0x4387B110) + 0x4387A770 == 0x43EF71A4
    assert word(0x436BEC70) + 0x436BEC56 == 0x43E77CCC
    assert word(0x43793730) + 0x4379347E + 0x5CC == 0x43E9BB14
    assert word(0x4378F9CC) + 0x4378FF6A == 0x43E9BAEC
    assert word(0x4378FD64) + 0x4378FA90 == 0x43E9B548
    assert word(0x4378FD70) + 0x4378FB8E == 0x43E99208
    table = blob[0x4387A6D4 - 0x43541000:0x4387A6D8 - 0x43541000]
    assert list(table) == [2, 4, 6, 8]
    assert [0x4387A6D4 + value * 2 for value in table] == [
        0x4387A6D8, 0x4387A6DC, 0x4387A6E0, 0x4387A6E4,
    ]
    initial = json.loads((OUT / "s39-initial.json").read_text())
    functions = {row.get("entry"): row for row in initial["functions"]}
    assert len(functions["43814d24"]["references"]) == 3
    for entry in ["43814ea0", "43815210", "43815560"]:
        assert "FUN_43814d24" in functions[entry]["pseudo_code"]
        assert "thunk_FUN_4387a1fc" in functions[entry]["pseudo_code"]
    consumers = json.loads((OUT / "s39-consumers.json").read_text())
    functions = {row.get("entry"): row for row in consumers["functions"]}
    listing = functions["4387a6c4"]["listing"]
    for instruction in ["4387a6d8 movs r3,#0x0", "4387a6dc movs r3,#0x1",
                        "4387a6e0 movs r3,#0x2", "4387a6e4 movs r3,#0x4"]:
        assert instruction in listing
    registers = json.loads((OUT / "s39-registers.json").read_text())
    writer = next(row for row in registers["functions"] if row["query"] == "43793400")
    assert writer["entry"] == "43792a0c"
    for instruction in ["437934b4 str.w r1,[r7,#0x5cc]",
                        "4379357c str.w r2,[r3,#0x5cc]",
                        "437935aa str.w r3,[r7,#0x5cc]",
                        "437935ea str.w r2,[r3,#0x5cc]"]:
        assert instruction in writer["listing"]
    context = json.loads((OUT / "s39-context.json").read_text())
    initializer = next(row for row in context["functions"] if row.get("entry") == "43ae8d56")
    assert "param_2[2] = param_1 + 0x5a4" in initializer["pseudo_code"]
    for name in findings["exports"]:
        data = json.loads((OUT / name).read_text())
        assert data["sha256"] == SHA
        assert all(f.get("completed") or f.get("status") == "listing_only_no_function"
                   for f in data["functions"])
    for name in ["s38-project-before.sha256", "s38-rep-before.sha256"]:
        for line in (OUT / name).read_text().splitlines():
            digest, filename = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest
    assert findings["physical_capture"] == "NO_VERIFICADO"
    print("| Hallazgo | Clasificación | Evidencia/resultado |")
    print("|---|---|---|")
    for row in findings["summary"]:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
