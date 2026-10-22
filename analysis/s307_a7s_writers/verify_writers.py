#!/usr/bin/env python3
"""S307: recompute signatures, absence counts and direct callers from the blobs."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A6 = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
             "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
DATA = Path(__file__).with_name("writers.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def callers(blob, target):
    out = []
    for a in range(0x43541000, 0x43D00000, 2):
        off = a - BASE
        if off + 4 > len(blob):
            break
        hw1 = blob[off] | (blob[off + 1] << 8)
        if (hw1 & 0xF800) != 0xF000:
            continue
        ins = next(MD.disasm(blob[off:off + 4], a), None)
        if ins and ins.mnemonic in ("bl", "blx", "b", "b.w") and ins.op_str == f"#0x{target:x}":
            out.append(f"0x{a:08x}")
    return out


def main():
    a7, a6 = A7.read_bytes(), A6.read_bytes()
    d = json.loads(DATA.read_text())
    assert d["firmware"]["a6000"] == hashlib.sha256(a6).hexdigest()
    assert d["firmware"]["a7s"] == hashlib.sha256(a7).hexdigest()

    def sig(site):
        s = site - 8
        return a7[s - BASE:s - BASE + 24].hex()

    for row in d["writers"]:
        for w in row["write_sites"]:
            site = int(w["site"], 16)
            assert sig(site) == w["signature_hex"], w["site"]
            assert a6.count(bytes.fromhex(w["signature_hex"])) == w["a6000_signature_hits"]
        for c in row["callers"]:
            assert c in callers(a7, int(row["function"], 16)), (row["function"], c)

    for row in d["reads_only"]:
        for w in row["sites"]:
            assert sig(int(w["site"], 16)) == w["signature_hex"]
            assert a6.count(bytes.fromhex(w["signature_hex"])) == w["a6000_signature_hits"]

    sel = int(d["selector"]["entry"], 16)
    assert a7[sel - BASE:sel - BASE + 4].hex() == d["selector"]["bytes_hex"]
    ins = next(MD.disasm(bytes.fromhex(d["selector"]["bytes_hex"]), sel), None)
    assert f"{ins.mnemonic} {ins.op_str}" == d["selector"]["insn"]
    assert callers(a7, sel) == d["selector"]["callers_direct"]

    tf = int(d["timing_function"]["entry"], 16)
    assert callers(a7, tf) == d["timing_function"]["direct_callers"] == []

    absent = [w["site"] for r in d["writers"] for w in r["write_sites"]
              if w["a6000_signature_hits"] == 0]
    print(f"OK: {len(absent)} stores A7S sin firma en A6000; "
          f"selector con {len(d['selector']['callers_direct'])} callers")


if __name__ == "__main__":
    main()
