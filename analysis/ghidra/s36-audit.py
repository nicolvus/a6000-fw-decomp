"""Comprueba identidad, aislamiento y cobertura de la evidencia S36."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AREA = ROOT / "analysis/ghidra"
SOURCE = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libInfraScalarMpr.so"
EXPECTED = "b56b4c6172a60b879ebf405bc64e19e7456d230ff6125a21bbd4469e35c0d2c9"


def main() -> None:
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    digest = hashlib.sha256()
    files = sorted([AREA / "silent-liro.gpr", *(AREA / "silent-liro.rep").rglob("*")])
    for path in files:
        if path.is_file():
            digest.update(str(path.relative_to(AREA)).encode())
            digest.update(path.read_bytes())
    assert digest.hexdigest() == "2e417daf633fc6986694466da6235d20ac741c8a2053682fe3633a2bd2925350"
    export = json.loads((AREA / "s36-library.json").read_text())
    assert export["executable_sha256"].lower() == EXPECTED
    rows = export["functions"]
    for address in ("00027f64", "00027ffc", "00027f28", "00028090", "00030700", "0003076c"):
        row = next(row for row in rows if row["entry"] == address)
        assert row["completed"], row
        assert row["listing"] and row["pseudo_code"]
    shared = next(row for row in rows if row["entry"] == "0003076c")["pseudo_code"]
    assert "shmget(0,param_1,0x3b6)" in shared and "shmat(" in shared
    symbols = (AREA / "s36-symbols.txt").read_text()
    assert "U DmmAccess::AllocDmmMemory(int, unsigned short*)" in symbols
    assert "U DmmAccess::FreeDmmMemory(int)" in symbols
    print("PASS: SHA firmware, proyecto av-cam intacto, SHA importación, seis funciones completas, SysV e importaciones UND")


if __name__ == "__main__":
    main()
