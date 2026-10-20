"""Audita identidades S42 e integridad sin ejecutar firmware."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    findings = json.loads((OUT / "s42-findings.json").read_text())
    blob = (ROOT / findings["binary"]).read_bytes()
    assert hashlib.sha256(blob).hexdigest() == SHA

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    def functions(name: str) -> dict:
        data = json.loads((OUT / name).read_text())
        assert data["sha256"] == SHA
        return {row["query"]: row for row in data["functions"]}

    identity = functions("s42-identity.json")
    assert identity["436d6320"]["entry"] != identity["436d6f6c"]["entry"]
    assert "436d6348 ldr r3,[r3,#0x28]" in identity["436d6320"]["listing"]
    assert "436d634a blx r3" in identity["436d6320"]["listing"]
    assert word(0x43FCC090 + 0x28) == 0x436D6F6D
    base = (word(0x436D7470) + 0x436D72FC) & 0xFFFFFFFF
    assert word((base + word(0x436D7474)) & 0xFFFFFFFF) + 8 == 0x43FCC090
    linear = json.loads((OUT / "s42-linear.json").read_text())[0]["temporary_listing"]
    assert "436d7136 ldrb.w r2,[r10,#0x8]" in linear
    assert "436d7142 ldrb.w r2,[r10,#0x14]" in linear
    assert "436d71e0 strh.w r3,[r4,#0x3a0]" in linear
    producer = functions("s42-config-copy.json")["4382dd78"]["listing"]
    assert "4382e3a8 strb.w r3,[r7,#0x36]" in producer
    assert "4382e3ae ldrb.w r3,[r3,#0x95]" in producer
    assert (word(0x43793740) + 0x43793538) & 0xFFFFFFFF == 0x43E9B548
    assert 0x43E9B548 + 0x5CC == 0x43E9BAEC + 0x28
    assert findings["physical_capture"] == "NO_VERIFICADO"
    assert findings["static_frontier_exhausted"] is False
    for filename in ("s38-project-before.sha256", "s38-rep-before.sha256"):
        for line in (OUT / filename).read_text().splitlines():
            digest, path = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    print("S42 PASS: despacho virtual, bytes clase2, productor, identidad R, SHA y proyecto")


if __name__ == "__main__":
    main()
