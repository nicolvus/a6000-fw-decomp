"""Contrasta las instrucciones A7S que producen CAIF[0x12]."""

import hashlib
import json
from pathlib import Path
from typing import Any

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[2]
BINARY = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                 "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


def audit(data: bytes) -> dict[str, Any]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    # R4 es el quinto argumento: 36 B guardados + 0x94 B locales = 0xb8.
    expected = {
        0x4382827A: ("ldr.w", "r2, [r2, #0xe8]"),
        0x43828282: ("adds", "r2, #0x40"),
        0x4382828C: ("str", "r2, [sp]"),
        0x43828292: ("add.w", "r1, r4, #0x20"),
        0x43828298: ("bl", "#0x43862e24"),
        0x43862E24: ("push.w", "{r4, r5, r6, r7, r8, sb, sl, fp, lr}"),
        0x43862E28: ("sub", "sp, #0x94"),
        0x43862E32: ("mov", "r6, r1"), 0x43862E3C: ("ldr", "r4, [sp, #0xb8]"),
        0x43863294: ("ldrb", "r3, [r2]"), 0x43863296: ("cmp", "r3, #0"),
        0x43863298: ("bne", "#0x43863398"),
        0x4386329A: ("ldr.w", "r2, [r6, #0x76c]"),
        0x4386329E: ("sub.w", "r1, r2, #2"),
        0x438632A2: ("rsbs", "r2, r1, #0"),
        0x438632A4: ("adc.w", "r2, r2, r1"),
        0x438632AC: ("lsls", "r2, r2, #5"),
        0x438632AE: ("cmp", "r1, #1"), 0x438632B0: ("it", "eq"),
        0x438632B2: ("adds", "r2, #1"),
        0x438632B4: ("strb", "r2, [r4, #0x12]"),
        0x43863398: ("movs", "r3, #1"),
        0x4386339A: ("strb", "r3, [r4, #0x12]"),
        0x43826DEE: ("ldr.w", "r2, [r4, #0x78c]"),
        0x43826DF2: ("bl", "#0x43826d58"),
    }
    for address, pair in expected.items():
        ins = next(decoder.disasm(data[address - BASE:address - BASE + 4], address, count=1))
        assert (ins.mnemonic, ins.op_str) == pair, (hex(address), ins.mnemonic, ins.op_str)
    return {
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "constructor": "0x43862e24", "caller": "0x4382822c",
        "payload_store": "0x438632b4", "payload": "*(root+0x4ae8)+0x40 (when nonnull)",
        "capture_selector": "root+0x78c == (root+0x20)+0x76c",
        "normal_bit_0x20_condition": "selector == 2",
        "normal_byte": "32 * (selector == 2) + (other_flag == 1)",
        "diagnostic_override": 1,
        "limits": "Normal path requires enabled payload and zero diagnostic override. "
                  "Sensor-mode selection has earlier bypasses and later overrides.",
        "sensor_modes": ["0x4e", "0x4f"], "physical_delivery": "NO_VERIFICADO",
    }


if __name__ == "__main__":
    print(json.dumps(audit(BINARY.read_bytes()), indent=2))
