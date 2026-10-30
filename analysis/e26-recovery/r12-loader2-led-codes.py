"""E26-R12 — Offline: decode the Loader2 (FUN_c01f3b74) and BootROM (FUN_ffff0d62) LED error encodings
from the bytes in the existing dumps and list where each negative error literal is consumed.
Static only; reads dump files, never touches the camera."""

import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "camera-dumps/updater-20261020-175427/bootloader.bin"
LBASE, LOFF = (
    0xC01F0000,
    0x22800,
)  # file offset = addr - LBASE + LOFF (verified by r7b bytechecks)


# Codes passed to FUN_ffff0d62 (callers 0fe6..126e + returns of 028c/02c6/044e/0486/0876 chain), r12 report §6.
# 0x4001 at ffff1324 is a register constant (str r1,[r4,#0xe0]), NOT an error code.
BOOTROM_ERROR_CODES = (
    *range(0x1001, 0x100F),
    *range(0x2001, 0x2006),
    *range(0x3001, 0x3005),
)


def led_pattern_loader2(err: int) -> tuple[int, int, int]:
    """FUN_c01f3b74: n=-err; thousands (slowest), hundreds (delay>>2), n%100 (delay>>3)."""
    n = -err
    return n // 1000, (n % 1000) // 100, n % 100


def led_pattern_bootrom(code: int) -> tuple[int, int]:
    """FUN_ffff0d62: (code>>12)-1 slow, code&0xfff fast."""
    return (code >> 12) - 1, code & 0xFFF


def literal_users(data: bytes, wanted: set[int]) -> dict[int, list[str]]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out: dict[int, list[str]] = {}
    a = LOFF
    end = LOFF + 0x20000
    while a < end:
        step = 2
        for i in md.disasm(data[a : a + 4], a - LOFF + LBASE, 1):
            step = i.size
            if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
                imm = int(i.op_str.split("#")[1].rstrip("]"), 16)
                lit = ((i.address + 4) & ~3) + imm
                w = struct.unpack(
                    "<I", data[lit - LBASE + LOFF : lit - LBASE + LOFF + 4]
                )[0]
                if w - (1 << 32) in wanted:
                    out.setdefault(w - (1 << 32), []).append(f"{i.address:#x}")
        a += step
    return out


if __name__ == "__main__":
    assert led_pattern_loader2(-302) == (0, 3, 2)
    assert led_pattern_bootrom(0x4002) == (3, 2) and led_pattern_bootrom(0x2005) == (
        1,
        5,
    )
    data = LOADER.read_bytes()
    users = literal_users(data, {-210, -302, -304, -306, -308})
    for e, v in sorted(users.items()):
        print(e, led_pattern_loader2(e), v)
    print(
        "bootrom codes:",
        {
            hex(c): led_pattern_bootrom(c)
            for c in (0x1001, 0x1004, 0x1005, 0x2001, 0x2005)
        },
    )
    print(
        "bootrom reaches 3 slow:",
        any(led_pattern_bootrom(c)[0] >= 3 for c in BOOTROM_ERROR_CODES),
    )
    sys.exit(0)
