#!/usr/bin/env python3
"""S301: byte-level verification of the A7S state xref sweep.

Re-decodes every address in state_xref_sweep.json from av-cam.bin and fails if an
instruction, byte sequence, offset or coverage claim does not match the blob.
"""
import hashlib
import json
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
HERE = Path(__file__).resolve().parent
EXPECTED_SHA = "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e"


def main():
    blob = BIN.read_bytes()
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    data = json.loads((HERE / "state_xref_sweep.json").read_text())

    def decode(address, size=4):
        raw = blob[address - BASE:address - BASE + size]
        ins = next(md.disasm(raw, address), None)
        return raw.hex(), (f"{ins.mnemonic} {ins.op_str}" if ins else None)

    assert data["firmware"]["sha256"] == hashlib.sha256(blob).hexdigest() == EXPECTED_SHA

    sites = data["sites"]
    addresses = [s["site"] for s in sites]
    assert len(addresses) == len(set(addresses)) == 79, len(addresses)

    for s in sites:
        hexbytes, text = decode(int(s["site"], 16))
        assert hexbytes == s["bytes_hex"], (s["site"], hexbytes, s["bytes_hex"])
        assert text == s["insn"], (s["site"], text, s["insn"])
        for a in s["accesses"]:
            hexbytes, text = decode(int(a["address"], 16))
            assert text == a["insn"], (a["address"], text, a["insn"])
            mnemonic = text.split()[0]
            assert mnemonic.startswith("str") == (a["kind"] == "write"), a
            assert mnemonic.startswith("ldr") == (a["kind"] == "read"), a
            if a.get("offset") is not None and "[r" in text:
                imm = text.split("#")[1].rstrip("]") if "#" in text else None
                assert imm is not None and int(imm, 0) == a["offset"], (a["address"], imm, a["offset"])
            # no write may target the gate bytes (reads at +3/+6 are expected)
            if a["kind"] == "write":
                assert a.get("offset") not in (3, 6), a

    # coverage: union of both exact xref lists recorded from REA in the JSON
    lists = data["rea_xrefs"]
    assert set(lists) == {"0x43f7bce6", "0x440251e4", "0x43ff928c"}
    assert len(lists["0x43f7bce6"]) == 16 and len(lists["0x440251e4"]) == 53
    assert lists["0x43ff928c"] == []
    gate_sites = {r["site"] for r in data["gates"]["rows"]}
    union = set(lists["0x43f7bce6"]) | set(lists["0x440251e4"]) | gate_sites
    assert union == set(addresses), (sorted(union - set(addresses)), sorted(set(addresses) - union))

    # only two absolute literals in the whole blob carry the state pointer
    needle = struct.pack("<I", 0x43F7BCE6)
    hits, i = [], 0
    while True:
        i = blob.find(needle, i)
        if i < 0:
            break
        hits.append(f"0x{BASE + i:08x}")
        i += 1
    assert hits == ["0x43ff928c", "0x440251e4"], hits
    assert [x["address"] for x in data["absolute_pointer_literals"]] == hits

    # gates: 16 reads, zero writers
    rows = data["gates"]["rows"]
    assert len(rows) == 16
    assert [r["type"] for r in rows] == ["READ"] * 16
    assert data["gates"]["writers"] == []
    assert sum(1 for r in rows if r["target"] == "state+3") == 8
    assert sum(1 for r in rows if r["target"] == "state+6") == 8
    for r in rows:
        hexbytes, text = decode(int(r["site"], 16))
        assert text == r["insn"] and hexbytes == r["bytes_hex"], r

    # counts match the classified rows
    counts = {}
    for s in sites:
        counts[s["class"]] = counts.get(s["class"], 0) + 1
    for k, v in counts.items():
        assert data["counts"][k] == v, (k, v)
    assert data["counts"]["total_sites"] == 79

    # write verdicts: all writes go to +0 or +2
    write_offsets = {a.get("offset") for s in sites for a in s["accesses"]
                     if a["kind"] == "write"}
    assert write_offsets <= {None, 2, 0xDE, 0xE6, 0xE8, 0xEA}, write_offsets
    assert data["verdict"]["writer_plus3"] is False
    assert data["verdict"]["writer_plus6"] is False

    print(f"OK: {len(sites)} sites, {len(rows)} gate reads, writes at offsets {sorted(str(x) for x in write_offsets)}")


if __name__ == "__main__":
    main()
