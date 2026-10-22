#!/usr/bin/env python3
"""S152: decode the descriptor entries that point into an IMX210 row gap."""
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("descriptor_reads.json")
TABLES = ((0x44008028, 68, 32), (0x4400B248, 59, 6))


def main():
    blob = BIN.read_bytes()
    descriptors = []
    for table, count, index in TABLES:
        raw_table = blob[table - BASE:table - BASE + count * 8]
        if len(raw_table) != count * 8:
            raise ValueError(f"short table at {table:#x}")
        rows = [struct.unpack_from("<HHI", raw_table, i * 8) for i in range(count)]
        if rows[-1] != (0, 0, 0):
            raise AssertionError(f"missing zero terminator in table {table:#x}")
        ident, size, address = rows[index]
        descriptors.append({
            "table_address": f"0x{table:08x}",
            "table_file_offset": f"0x{table - BASE:x}",
            "entry_count_including_terminator": count,
            "terminator_index": count - 1,
            "target_index": index,
            "target_entry_address": f"0x{table + index * 8:08x}",
            "entry_raw_hex": raw_table[index * 8:index * 8 + 8].hex(),
            "entry_fields": {
                "id_u16_le": f"0x{ident:04x}",
                "size_u16_le": size,
                "address_u32_le": f"0x{address:08x}",
            },
        })
    result = {
        "milestone": "S152",
        "firmware_sha256": hashlib.sha256(blob).hexdigest(),
        "base": f"0x{BASE:08x}",
        "descriptor_schema_observed_by_bytes": "{u16 id, u16 size, u32 address}, little-endian; 8 bytes",
        "matching_entries": descriptors,
        "rea": {
            "raw_copy_formatter": "0x43b09c7a reads address+size-1 downward and writes into caller buffer",
            "size_one_result": "reads exactly one byte at address 0x43eb0850",
            "reachability": "two caller-side gates are statically identified; their runtime values are unknown",
            "write_effect": "the identified copier writes the destination buffer, not the source address",
        },
        "evidence_ids": {
            "table_a_entry": "ev_f8bd0f66f1e8d90f997d6ea0c37e47e3911c40c8dc9de66f9652bfca536f4289",
            "table_b_entry": "ev_01d929687b87aa4343c193261123044fac8ffad3ae264dda33a77826adfffa90",
            "consumer_copier": "ev_2d31ad1d2d49ace2985775034cfc294bb17251c7e6930056dfb4cb9c47716ffa",
            "consumer_hex_formatter": "ev_6efbdb9318dab3f4c890adbbc9f1e066ffa8905d6ccb639967336a706653e212",
            "caller_gates": "ev_f944e886a327ba29e26b3daefbb015d751b348023b937b6ee1eae21ed370ddc3",
            "gate_state_zero_in_blob": "ev_bb32443f6fbf218e8e633251877e90f9a85a57324d21e818d58e4f45a8d72c0f",
        },
        "scope_limit": "Identified static diagnostic-copy path only; it does not establish runtime reachability or global absence of other writers/readers.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(descriptors)} matching descriptor entries")


if __name__ == "__main__":
    main()
