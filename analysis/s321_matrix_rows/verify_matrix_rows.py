#!/usr/bin/env python3
"""Comprobaciones independientes sobre los bytes y el JSON de S321."""
from __future__ import annotations

import json
import struct
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6000 = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
DATA = Path(__file__).with_name("matrix_rows.json")
checks = 0


def ok(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def u32(blob: bytes, address: int) -> int:
    return struct.unpack_from("<I", blob, address - BASE)[0]


def count_rows(blob: bytes, start: int) -> tuple[int, int]:
    count = 0
    address = start
    while u32(blob, address):
        pointer = u32(blob, address)
        ok(BASE <= pointer < BASE + len(blob), f"puntero de fila {address:#x}")
        count += 1
        address += 0x14
    return count, address


def main() -> None:
    data = json.loads(DATA.read_text())
    a7s = A7S.read_bytes()
    a6000 = A6000.read_bytes()
    count, end = count_rows(a7s, 0x43FEE598)
    ok((count, end) == (69, 0x43FEEAFC), "69 filas A7S")
    ok(u32(a7s, 0x43FEE598) == 0x44021FF2, "fila omitida por S314")
    ok(u32(a7s, 0x44028844) == 0x43FEE598, "slot GOT de matriz")
    ok(u32(a7s, 0x43FCE0F0) & ~1 == 0x436F3928, "slot vtable +0xa0")
    mode_map = a7s[0x43C9C5B5 - BASE : 0x43C9C5B5 - BASE + 0x52]
    ok(mode_map[0x4E] == mode_map[0x4F] == 1, "silent usa columna 1")
    loop = a7s[0x436F393A - BASE : 0x436F3948 - BASE]
    ok(loop.hex() == "551814322d7925701468002cf8d1", "bucle consumidor")
    count_a6000, end_a6000 = count_rows(a6000, 0x43FE9B74)
    ok((count_a6000, end_a6000) == (59, 0x43FEA010), "59 filas A6000")
    ok(data["matrix_a7s"]["rows"] == count, "JSON A7S")
    ok(data["consumer_a7s"]["slot2_bytes_nonzero"] == 0, "overlay sin bytes")
    ok(data["mode_columns"]["any_column_exclusive_to_silent"] is False, "columna no exclusiva")
    print(f"OK S321: {checks} comprobaciones")


if __name__ == "__main__":
    main()
