"""Comprueba evidencia S38 sin ejecutar firmware ni escribir el proyecto."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
BLOB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    data = BLOB.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SHA
    assert data[4:8] == b"ORIL" and data[:4] != b"\x7fELF"
    def word(address: int) -> int:
        return int(struct.unpack_from("<I", data, address - 0x43541000)[0])
    assert word(0x43541014) == 0x435410B4
    assert word(0x43541398) == word(0x43541294) == 0
    assert word(0x43561538) + 0x4356152E + word(0x4356153C) == 0x440205C0
    assert word(0x440205C0) == 0x43541000
    for manifest in ["s38-project-before.sha256", "s38-rep-before.sha256"]:
        for line in (OUT / manifest).read_text().splitlines():
            digest, filename = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest
    for args in [["readelf", "-dW"], ["readelf", "-rW"], ["nm", "-D"], ["nm"]]:
        result = subprocess.run([*args, str(BLOB)], capture_output=True, check=False)
        assert result.returncode != 0
    exported = json.loads((OUT / "s38-transport.json").read_text())
    functions = {row.get("entry"): row for row in exported["functions"]}
    assert "param_1 + -4" in functions["43a49adc"]["pseudo_code"]
    assert "param_1 + 0xc" in functions["43a49628"]["pseudo_code"]
    scan = json.loads((OUT / "s38-scan.json").read_text())
    assert len(scan["literal_hits"]) == 85
    assert sum(not hit["references"] for hit in scan["literal_hits"]) == 16
    assert sum(row.get("completed", False) for row in scan["functions"]) == 72
    assert all(row["completed"] for row in exported["functions"])
    assert any("+ 0x2e4" in row.get("pseudo_code", "") for row in scan["functions"])
    findings = json.loads((OUT / "s38-findings.json").read_text())
    assert findings["physical_yc"] == "NO_VERIFICADO"
    print("PASS: SHA, ORIL, PIC, slots vacíos, proyecto intacto, herramientas ELF y transporte")
    print("| Validación | Estado | Resultado |")
    print("|---|---|---|")
    for row in findings["summary"]:
        print("| " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
