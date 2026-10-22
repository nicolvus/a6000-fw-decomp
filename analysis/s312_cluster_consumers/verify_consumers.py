#!/usr/bin/env python3
"""S312: re-check consumer sites and function absence."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("consumers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["a6000"] == hashlib.sha256(a6).hexdigest()
    assert d["firmware"]["a7s"] == hashlib.sha256(a7).hexdigest()
    for row in d["site_rows"]:
        a = int(row["site"], 16)
        ins = next(MD.disasm(a7[a - BASE:a - BASE + 4], a), None)
        assert ins.mnemonic.startswith("ldr") or ins.mnemonic.startswith("ldrb"), row["site"]
        assert row["a6000_hits"] == 0
    for f in d["functions"]:
        addr = int(f["function"], 16)
        head = a7[addr - BASE:addr - BASE + 24]
        assert head.hex() == f["head_hex"]
        assert a6.count(head) == f["a6000_hits"] == 0
    fields = {x for r in d["site_rows"] for x in r["fields"]}
    assert {0xAE if False else "+0xae", "+0xde", "+0xdf", "+0xe0", "+0xe2", "+0xe4", "+0xe6"} <= fields
    print(f"OK: {len(d['functions'])} funciones consumidoras, todas ausentes en A6000")


if __name__ == "__main__":
    main()
