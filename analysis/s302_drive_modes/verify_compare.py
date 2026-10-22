#!/usr/bin/env python3
"""S302: re-decode every claim of compare.json from the two firmware blobs."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BLOBS = {
    "a6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
    "a7s": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                   "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
DATA = Path(__file__).with_name("compare.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    data = json.loads(DATA.read_text())
    blobs = {k: v.read_bytes() for k, v in BLOBS.items()}

    for fw, blob in blobs.items():
        assert data["firmware"][fw]["sha256"] == hashlib.sha256(blob).hexdigest()

    for c in data["claims"]:
        blob = blobs[c["firmware"]]
        addr = int(c["address"], 16)
        raw = blob[addr - BASE:addr - BASE + 4]
        ins = next(MD.disasm(raw, addr), None)
        assert raw.hex() == c["bytes_hex"], (c["label"], raw.hex(), c["bytes_hex"])
        assert ins is not None and f"{ins.mnemonic} {ins.op_str}" == c["insn"], \
            (c["label"], f"{ins.mnemonic} {ins.op_str}", c["insn"])

    # matrices: stride 20, 4-byte header, 16-byte payload, zero header terminates
    for fw, spec in data["matrices"].items():
        blob = blobs[fw]
        base = int(spec["addr"], 16)
        assert spec["stride"] == 20 and spec["header_bytes"] == 4 and spec["payload_bytes"] == 16
        for row in spec["rows"]:
            raw = blob[base - BASE + 20 * row["index"]: base - BASE + 20 * row["index"] + 20]
            assert raw[4:].hex() == row["payload_hex"], (fw, row["index"])
            assert f"0x{int.from_bytes(raw[:4], 'little'):08x}" == row["header"]
        # the row after the last one must be the zero terminator
        last = len(spec["rows"])
        raw = blob[base - BASE + 20 * last: base - BASE + 20 * last + 4]
        assert int.from_bytes(raw, "little") == 0, (fw, "no terminator")
    assert len(data["matrices"]["a6000"]["rows"]) == 59
    assert len(data["matrices"]["a7s"]["rows"]) == 69

    # A7S mode list: 34 u32 codes, then the register rows start
    ml = data["mode_list"]
    blob = blobs["a7s"]
    base = int(ml["addr"], 16)
    assert len(ml["codes"]) == 34
    for k, code in enumerate(ml["codes"]):
        raw = blob[base - BASE + 4 * k: base - BASE + 4 * k + 4]
        assert int.from_bytes(raw, "little") == code
    assert ml["codes"][29] == 0x4E and ml["codes"][30] == 0x4F
    assert ml["codes"][27] == 0x4C and ml["codes"][28] == 0x4D

    # mode -> column map
    mm = data["mode_map"]
    raw = blob[int(mm["addr"], 16) - BASE: int(mm["addr"], 16) - BASE + mm["count"]]
    assert raw.hex() == mm["bytes"]
    for k, v in mm["columns_for_modes"].items():
        assert raw[int(k, 16)] == v, (k, raw[int(k, 16)], v)
    # silent modes share the register column with 0x4c/0x4d
    for mode in (0x4C, 0x4D, 0x4E, 0x4F):
        assert raw[mode] == 1, (hex(mode), raw[mode])

    # selector returns claimed codes
    sel = {c["label"]: c["insn"] for c in data["claims"] if c["firmware"] == "a7s"}
    assert sel["a7s_selector_4e"].endswith("#0x4e")
    assert sel["a7s_selector_4f"].endswith("#0x4f")
    assert sel["a7s_selector_0b"].endswith("#0xb")
    assert sel["a7s_selector_35"].endswith("#0x35")
    assert sel["a7s_selector_17"].endswith("#0x17")

    print(f"OK: {len(data['claims'])} claims, matrices 59/69 rows, 34 modos, "
          f"mapa 0x{mm['count']:02x} bytes")


if __name__ == "__main__":
    main()
