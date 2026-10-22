#!/usr/bin/env python3
"""S303: re-derive the table and every call edge from av-cam.bin."""
import hashlib
import json
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
DATA = Path(__file__).with_name("ref_tree.json")
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def main():
    blob = BIN.read_bytes()
    data = json.loads(DATA.read_text())
    assert data["firmware"]["sha256"] == hashlib.sha256(blob).hexdigest()

    def read(addr, size=4):
        return blob[addr - BASE:addr - BASE + size]

    def dis(addr):
        ins = next(MD.disasm(read(addr), addr), None)
        return f"{ins.mnemonic} {ins.op_str}" if ins else None

    t = int(data["table"]["base"], 16)
    vals = []
    for k in range(400):
        v = int.from_bytes(read(t + 4 * k), "little")
        if not (0x43540000 <= v < 0x44100000):
            break
        vals.append(v)
    assert len(vals) == data["table"]["entries"] == 148
    assert data["table"]["terminator"] == f"0x{t + 4 * len(vals):08x}"
    assert len(set(vals)) == len(vals) == 148
    assert data["table"]["state_index"] == 18
    assert vals[18] == 0x43F72D02
    assert data["table"]["state_entry"] == f"0x{t + 4 * 18:08x}" == "0x43ff3248"
    assert min(vals) == int(data["table"]["min"], 16)
    assert max(vals) == int(data["table"]["max"], 16)
    assert all(v >= 0x43E00000 for v in vals) == data["table"]["all_entries_are_bss_objects"]

    slot = int(data["table"]["got_slot"]["address"], 16)
    assert int.from_bytes(read(slot), "little") == t

    def check(edge):
        addr = int(edge["site"], 16)
        assert read(addr).hex() == edge["bytes_hex"], edge["site"]
        assert dis(addr) == edge["insn"], (edge["site"], dis(addr))
        assert edge["target"] in edge["insn"]
        return addr

    for e in data["dumper"]["direct_callers"]:
        check(e)
    assert len(data["dumper"]["direct_callers"]) == 2
    assert {e["site"] for e in data["dumper"]["direct_callers"]} == {"0x43859868", "0x43859892"}
    assert dis(0x43858338).startswith("push")

    for e in data["caller_function"]["callers"]:
        check(e)
    assert len(data["caller_function"]["callers"]) == 10
    for u in data["got_users"]:
        addr = int(u["site"], 16)
        assert read(addr).hex() == u["bytes_hex"]
        assert dis(addr) == u["insn"]
    assert data["rea"]["dumper_callers"] == ["0x43859710"]
    assert data["rea"]["slot_0x4401f080_xrefs"] == []

    for group in data["level3"].values():
        for e in group:
            check(e)

    # the two addresses flagged as non-entries must NOT decode to a prologue
    for addr, what in ((0x438581E8, "corrections"), (0x43858390, "corrections")):
        assert read(addr).hex() == data[what][f"0x{addr:08x}"]["bytes_hex"]
        assert dis(addr) == data[what][f"0x{addr:08x}"]["insn"]
        assert not dis(addr).startswith("push"), addr

    print(f"OK: tabla {len(vals)} entradas, estado idx 18, "
          f"{len(data['dumper']['direct_callers'])} callers del dumper, "
          f"{len(data['caller_function']['callers'])} del caller")


if __name__ == "__main__":
    main()
