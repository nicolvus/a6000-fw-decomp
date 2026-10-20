"""Contrasta identidad del contexto, getter IMX210 e integridad de S45."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    blob = (ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == SHA
    findings = json.loads((OUT / "s45-findings.json").read_text())

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    assert (word(0x437B4EF8) + 0x437B4ECA) & 0xFFFFFFFF == findings["context"]
    assert findings["context"] == 0x43EAADD8
    assert word(0x43FCC090 + 0x74) == 0x43AD9203
    assert blob[0x43AD9202 - 0x43541000:0x43AD9208 - 0x43541000].hex() == "b0f8a0037047"
    assert (word(0x437943E4) + 0x4379408A) & 0xFFFFFFFF == findings["root_copy"]
    assert findings["root_copy"] + 0x1E6C == findings["c"]
    assert word(0x438C845C) == 1_000_000
    for filename in ("s38-project-before.sha256", "s38-rep-before.sha256"):
        for line in (OUT / filename).read_text().splitlines():
            digest, path = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    for name in ("context", "identity", "timing-use", "alias-builder", "vd-register"):
        data = json.loads((OUT / f"s45-{name}.json").read_text())
        assert data["sha256"] == SHA
        assert "Processing read-only project file: /av-cam.bin" in (OUT / f"s45-{name}.log").read_text()
    print("S45 PASS: SHA antes/después, memoria exportada, .gpr/.rep, contexto y getter+74")


if __name__ == "__main__":
    main()
