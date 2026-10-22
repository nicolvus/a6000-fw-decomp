#!/usr/bin/env python3
"""S308: re-decode the selector flow and the timing-function entry from the A7S blob."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("flow.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    blob = A7.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["sha256"] == hashlib.sha256(blob).hexdigest()

    for c in d["selector_site"]:
        a = int(c["address"], 16)
        raw = blob[a - BASE:a - BASE + 4]
        i = next(MD.disasm(raw, a), None)
        assert raw.hex() == c["bytes_hex"]
        assert f"{i.mnemonic} {i.op_str}" == c["insn"], c["label"]

    ptrs = []
    for i in range(len(blob) - 4):
        v = int.from_bytes(blob[i:i + 4], "little")
        if 0x43864000 <= v < 0x43865000:
            ptrs.append({"at": f"0x{BASE + i:08x}", "value": f"0x{v:08x}"})
    assert ptrs == d["pointers_into_0x43864xxx"]

    callers = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw = blob[off] | (blob[off + 1] << 8)
        if (hw & 0xF800) != 0xF000:
            continue
        i = next(MD.disasm(blob[off:off + 4], a), None)
        if i and i.mnemonic in ("bl", "blx", "b", "b.w") and i.op_str == "#0x438645bc":
            callers.append(f"0x{a:08x}")
    assert callers == d["timing_entry_direct_callers"]

    print(f"OK: selector con {len(d['selector_site'])} instrucciones, "
          f"{len(ptrs)} punteros a 0x43864xxx, caller {callers}")


if __name__ == "__main__":
    main()
