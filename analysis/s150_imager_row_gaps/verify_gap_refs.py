#!/usr/bin/env python3
"""S150: verify bytes for unreferenced row-gap addresses and literal pointers."""
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("gap_refs.json")
GAPS = (0x43EB0830, 0x43EB0831, 0x43EB0840, 0x43EB0841,
        0x43EB0850, 0x43EB0851, 0x43EB0860, 0x43EB0861)
TABLES = (0x4400812C, 0x4400B27C)


def main():
    blob = BIN.read_bytes()

    def read(address, size):
        offset = address - BASE
        raw = blob[offset:offset + size]
        if len(raw) != size:
            raise ValueError(f"short read at {address:#x}")
        return raw

    gaps = []
    for address in GAPS:
        raw = read(address, 2)
        gaps.append({
            "address": f"0x{address:08x}",
            "file_offset": f"0x{address - BASE:x}",
            "bytes_hex": raw.hex(),
        })
    tables = []
    for address in TABLES:
        raw = read(address, 16)
        words = struct.unpack("<4I", raw)
        tables.append({
            "address": f"0x{address:08x}",
            "file_offset": f"0x{address - BASE:x}",
            "bytes_hex": raw.hex(),
            "words_le": [f"0x{word:08x}" for word in words],
        })
    result = {
        "milestone": "S150",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "gaps": gaps,
        "tables_with_pointer_literal": tables,
        "rea": {
            "direct_xrefs_empty_at_each_gap": True,
            "xref_evidence_ids": [
                "ev_c42a7d7fd9a1e599c8d0b74992d387d3f1e7164896d259abe3a6ef0f7e68f68c",
                "ev_c1664bce2a3920c0c801a1aaff003ca91ccc4b4b8633f708cba8bdb44b125d34",
                "ev_fbcf9d3ee8809bd2b72d2e50e7052aa6f06e982d175373f0d17886c1686255d6",
                "ev_59e95069b0a10c85cd584c28412ab5fe83867491a6b91797175eaad10f6f1856",
                "ev_77d3f4ce807b15caecfc43cf8a05b1d15042431081d2c73161bdcf6783d672af",
                "ev_0c07447897f2035e5bde864612e549695f004dd7d302f953b2c89004188583d8",
                "ev_5fb7233ea97b868884f119553adfa2a46f25bf15aab56f3e5e2129d56116f6e6",
                "ev_55c7c05551f922a8af96f3b4d7dbae64da5be5e55e55eacc780eb55d0149416b",
            ],
            "positive_control": {
                "address": "0x43eb0848",
                "evidence_id": "ev_afcfff7678cf182ee835cd1ed4dfd1b2f55fdb0872a6bfc51817b3a9ab9f3b55",
                "xrefs": ["0x43836910", "0x43836916"],
                "instruction_evidence_ids": [
                    "ev_0e3051e04e63b42f37198d1ffd69bbe5f5a36c94f3632a2d5afd6cd431e7400d",
                    "ev_3134e5228b2566b14c6a9911612f9563b3350dab0b38e7d82336e41a12af955a",
                ],
            },
            "literal_search": {
                "pattern": "5008eb43",
                "evidence_id": "ev_201b0a5e0f16fe153da29642e861f41b0a7cebeb611865db65540927452d7668",
                "complete": True,
                "matches": ["0x4400812c", "0x4400b27c"],
            },
        },
        "conclusion_scope": "No direct xrefs to the eight exact gap bytes under this REA analysis. Literal pointer to 0x43eb0850 exists in data; it is not itself a classified read/write reference. Alias/parameterized accesses remain unknown.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(gaps)} gap bytes, {len(tables)} literal table records")


if __name__ == "__main__":
    main()
