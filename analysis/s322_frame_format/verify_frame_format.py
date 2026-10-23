#!/usr/bin/env python3
"""Verificacion independiente de bytes y tramas para S322."""
from __future__ import annotations

import json
from pathlib import Path

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
DATA = Path(__file__).with_name("frame_format.json")
SCENARIOS = ROOT / "analysis/s58/out/a7s_scenarios.json"
checks = 0


def ok(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise AssertionError(message)


def raw(blob: bytes, address: int, size: int) -> bytes:
    return blob[address - BASE : address - BASE + size]


def main() -> None:
    blob = A7S.read_bytes()
    data = json.loads(DATA.read_text())
    scenarios = json.loads(SCENARIOS.read_text())
    ok(raw(blob, 0x43AD966E, 4).hex() == "18f471ff", "call capacity")
    ok(raw(blob, 0x43AD967A, 4).hex() == "fff7d5ff", "call assembler")
    ok(raw(blob, 0x43AD967E, 4).hex() == "80f00100", "xor return")
    ok(raw(blob, 0x43AD9538, 2).hex() == "8122", "header 0x81")
    ok(raw(blob, 0x43AD9552, 4).hex() == "d2785a70", "device byte")
    ok(raw(blob, 0x43AD9568, 4).hex() == "05f8011b", "address byte")
    ok(raw(blob, 0x43AD95B2, 4).hex() == "05f8011b", "data byte")
    ok(raw(blob, 0x43AD93A0, 6).hex() == "013ad21a1a70", "length calculation")
    total = 0
    for scenario in scenarios:
        decoded = []
        for tx_hex in scenario["tx"]:
            tx = bytes.fromhex(tx_hex)
            position = 0
            while position < len(tx) and tx[position] != 0:
                ok(tx[position : position + 2] == b"\x81\x03", "frame 81|03")
                decoded.append(list(tx[position + 2 : position + 5]))
                position += 5
            ok(position == len(tx) - 1 and tx[position] == 0, "terminator 00")
        ok(decoded == scenario["device_seq"], "round-trip registros")
        total += len(decoded)
    observed = data["existing_emulation"]
    ok(observed["decoded_frames"] == observed["registers"] == total, "conteo JSON")
    ok(data["byte_aligned_frame"]["example"] == "810381001c", "ejemplo")
    print(f"OK S322: {checks} comprobaciones; {total} tramas")


if __name__ == "__main__":
    main()
