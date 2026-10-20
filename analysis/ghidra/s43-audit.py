"""Contrasta los resultados S43 con bytes originales y exports de solo lectura."""
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

    def word(address: int) -> int:
        return struct.unpack_from("<I", blob, address - 0x43541000)[0]

    base = (word(0x436D7298) + 0x436D6F84) & 0xFFFFFFFF
    assert base == 0x4401EEE4
    expected = [0x4401C7E0, 0x4401C678, 0x4401C744, 0x4401C684,
                0x4401C698, 0x4401C764]
    for literal, target in zip(range(0x436D72A0, 0x436D72B8, 4), expected):
        assert word((base + word(literal)) & 0xFFFFFFFF) == target
    assert [word(p) & 0xFFFF for p in expected] == [3, 4, 5, 6, 7, 8]
    assert blob[0x43CA2585 - 0x43541000:].startswith(
        b"[CAMERA_MAIN_SYNC]: SetSequenceMode img:%d, fratechg:%d, clamp:%d")
    for filename in ("s43-core.json", "s43-transport.json", "s43-registers.json", "s43-followup.json"):
        export = json.loads((OUT / filename).read_text())
        assert export["sha256"] == SHA
        for row in export["functions"]:
            if row.get("status") == "listing_only_no_function":
                assert row["query"] in {"436d92e0", "436d8ff4"}
            else:
                assert row.get("completed")
    core = json.loads((OUT / "s43-core.json").read_text())
    functions = {row["entry"]: row for row in core["functions"]}
    for address in ("43ad9a40", "43ad99d4"):
        listing = functions[address]["listing"]
        assert not any(" bl " in line or "blx" in line for line in listing)
    for filename in ("s38-project-before.sha256", "s38-rep-before.sha256"):
        for line in (OUT / filename).read_text().splitlines():
            digest, path = line.split(maxsplit=1)
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    print("S43 PASS: SHA, PIC, registros 3..8, cadena SetSequenceMode, setters y .gpr/.rep")


if __name__ == "__main__":
    main()
