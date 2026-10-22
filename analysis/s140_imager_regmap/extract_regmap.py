#!/usr/bin/env python3
"""S140: extrae y valida el vector IMX210 y los dos bancos BSS documentados."""
import hashlib
import json
import struct
from pathlib import Path

BASE = 0x43541000
PTR_TABLE = 0x43FE995C
BANKS = ((0x43EB35D0, 0x148), (0x43EB07FC, 0x100))
BIN = Path("analysis/rea-independent/input/av-cam.bin")
OUT = Path(__file__).with_name("imager_regmap.json")


def main():
    data = BIN.read_bytes()

    def read(address, size):
        offset = address - BASE
        if offset < 0 or offset + size > len(data):
            raise ValueError(f"address outside blob: {address:#x}+{size:#x}")
        return data[offset:offset + size]

    ptrs = []
    for i in range(120):
        pointer = struct.unpack("<I", read(PTR_TABLE + 4 * i, 4))[0]
        if pointer == 0:
            break
        ptrs.append(pointer)
    else:
        raise AssertionError("pointer table has no zero terminator in 120 slots")
    if len(ptrs) != 119:
        raise AssertionError(f"expected 119 pointers, got {len(ptrs)}")

    records = []
    for index, address in enumerate(ptrs):
        raw = read(address, 4)
        records.append({
            "index": index,
            "address": f"0x{address:08x}",
            "raw_hex": raw.hex(),
            "id_u16_le": struct.unpack_from("<H", raw)[0],
            "value_plus_2": raw[2],
            "byte_plus_3": raw[3],
        })

    banks = []
    for address, size in BANKS:
        raw = read(address, size)
        banks.append({
            "address": f"0x{address:08x}",
            "length": size,
            "raw_hex": raw.hex(),
            "all_zero_in_firmware_image": not any(raw),
            "rows_16_bytes": [raw[i:i + 16].hex() for i in range(0, size - size % 16, 16)],
            "trailing_bytes_hex": raw[size - size % 16:].hex(),
        })

    result = {
        "milestone": "S140",
        "firmware": "Sony A6000 fw3.21 av-cam.bin",
        "sha256": hashlib.sha256(data).hexdigest(),
        "base_address": f"0x{BASE:08x}",
        "file_offset_rule": "address - 0x43541000",
        "pointer_table": {
            "address": f"0x{PTR_TABLE:08x}",
            "pointer_count": len(ptrs),
            "terminator_address": f"0x{PTR_TABLE + 4 * len(ptrs):08x}",
            "terminator": 0,
            "records": records,
        },
        "banks": banks,
        "interpretation": {
            "verified": "Each pointed record begins with a little-endian u16 ID followed by bytes +2 and +3.",
            "unknown": "Physical sensor-register meanings and runtime bank contents are not established by these static bytes.",
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUT}: {len(records)} records, {len(banks)} bank ranges")


if __name__ == "__main__":
    main()
