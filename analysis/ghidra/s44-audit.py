"""Contrasta consumidor, tabla de modos, bancos MMIO e integridad S44."""
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
    findings = json.loads((OUT / "s44-findings.json").read_text())

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    assert word(0x43FCC090 + 0xA8) == 0x436D65B9
    assert word(0x44023598) == 0x43FE995C
    assert word(0x43FE9B38) == 0
    assert findings["register_count"] == (0x43FE9B38 - 0x43FE995C) // 4
    pointers = [word(0x43FE995C + i * 4) for i in range(119)]
    assert [word(p) & 0xFFFF for p in pointers[4:10]] == list(range(3, 9))
    modes = [word(0x43FEA070 + i * 4) for i in range(13)]
    assert findings["mode_codes"] == modes
    assert word(0x44025170) + 2 == word(0x43FE9B74)
    values = list(blob[0x43FE9B78 - 0x43541000:0x43FE9B85 - 0x43541000])
    assert findings["mode_bytes"] == values
    assert findings["high_nibbles"] == [value & 0xF0 for value in values]
    banks = [[word(0x43BC14E8 + i * 12 + j) for j in (0, 4, 8)] for i in range(3)]
    assert findings["mmio_banks"] == banks
    assert [word(0x43BC16D4 + i * 4) for i in range(3)] == [1, 2, 0]
    for filename in ("s38-project-before.sha256", "s38-rep-before.sha256"):
        for line in (OUT / filename).read_text().splitlines():
            digest, path = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    for name in ("s44-wire", "s44-mmio", "s44-encode", "s44-origin"):
        data = json.loads((OUT / f"{name}.json").read_text())
        assert data["sha256"] == SHA
        assert "Processing read-only project file: /av-cam.bin" in (OUT / f"{name}.log").read_text()
    print("S44 PASS: SHA, .gpr/.rep, 119 registros, 13 modos, virtual+a8 y bancos MMIO")


if __name__ == "__main__":
    main()
