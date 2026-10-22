#!/usr/bin/env python3
"""S311: re-check the A6000 config writers, their presence in the A7S and their callers."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("config.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def callers(blob, target):
    out = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw = blob[off] | (blob[off + 1] << 8)
        if (hw & 0xF800) != 0xF000:
            continue
        i = next(MD.disasm(blob[off:off + 4], a), None)
        if i and i.mnemonic in ("bl", "blx", "b", "b.w") and i.op_str == f"#0x{target:x}":
            out.append(f"0x{a:08x}")
    return out


def main():
    a6, a7 = A6.read_bytes(), A7.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["a6000"] == hashlib.sha256(a6).hexdigest()
    assert d["firmware"]["a7s"] == hashlib.sha256(a7).hexdigest()
    for row in d["writers"]:
        f = int(row["function"], 16)
        head = a6[f - BASE:f - BASE + 24]
        assert head.hex() == row["head_hex"]
        assert a7.count(head) == row["a7s_head_hits"]
        assert callers(a6, f) == row["callers"], row["function"]
        for s in row["write_sites"]:
            ins = next(MD.disasm(a6[int(s, 16) - BASE:int(s, 16) - BASE + 4],
                                 int(s, 16)), None)
            assert ins.mnemonic.startswith("str"), s
    shared = [r["function"] for r in d["writers"] if r["a7s_head_hits"] == 1]
    assert len(shared) == 2
    print(f"OK: {len(d['writers'])} writers A6000, {len(shared)} compartidos con A7S")


if __name__ == "__main__":
    main()
