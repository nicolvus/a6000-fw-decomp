"""Registra o contrasta las huellas de los artefactos protegidos de S46."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/ghidra"
FIRMWARE = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
EXPECTED = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def main() -> None:
    paths = [FIRMWARE, OUT / "silent-liro.gpr"]
    paths.extend(p for p in sorted((OUT / "silent-liro.rep").rglob("*")) if p.is_file())
    manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert manifest[str(FIRMWARE.relative_to(ROOT))] == EXPECTED
    phase = sys.argv[1]
    if phase == "after":
        assert manifest == json.loads((OUT / "s46-integrity-before.json").read_text())
    (OUT / f"s46-integrity-{phase}.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"S46 {phase}: SHA firmware correcto; {len(manifest)} archivos protegidos" )


if __name__ == "__main__":
    main()
