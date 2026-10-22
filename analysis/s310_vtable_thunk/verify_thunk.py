#!/usr/bin/env python3
"""S310: re-decode the thunk family and the selector call site."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("thunk.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    blob = A7.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["sha256"] == hashlib.sha256(blob).hexdigest()
    for row in d["thunks"]:
        a = int(row["entry"], 16)
        raw = blob[a - BASE:a - BASE + 12]
        assert raw.hex() == row["bytes_hex"], row["entry"]
        ins = [f"{i.mnemonic} {i.op_str}" for i in MD.disasm(raw, a)]
        assert ins[:4] == row["insn"], row["entry"]
        slots = [i for i in ins if "[" in i and "#0x" in i]
        assert row["vtable_slot"] == (slots[0].split("#")[1].rstrip("]") if slots else None)
    # selector result site
    a = 0x435490C4
    ins = next(MD.disasm(blob[a - BASE:a - BASE + 4], a), None)
    assert f"{ins.mnemonic} {ins.op_str}" == "bl #0x43ad9704"
    print(f"OK: {len(d['thunks'])} thunks, selector -> 0x43ad9704")


if __name__ == "__main__":
    main()
