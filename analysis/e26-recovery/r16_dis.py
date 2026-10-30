"""R16: desensamblador Thumb mínimo de Loader3 (bootloader.bin, VA 0xc01f0000..0xc0205800). Solo lectura."""

from __future__ import annotations

import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BL = (
    Path(__file__).resolve().parents[1]
    / "camera-dumps/updater-20261020-175427/bootloader.bin"
)
BASE_VA, FILE_OFF, END_VA = 0xC01F0000, 0x22800, 0xC0205800


def read(va: int, n: int) -> bytes:
    if not BASE_VA <= va and va + n <= END_VA:
        raise ValueError(f"{va:#x} fuera del prefijo analizable")
    o = FILE_OFF + va - BASE_VA
    return BL.read_bytes()[o : o + n]


def dis(va: int, n: int) -> list[str]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    return [
        f"{i.address:08x}: {i.mnemonic} {i.op_str}"
        for i in md.disasm(read(va & ~1, n), va & ~1)
    ]


if __name__ == "__main__":
    print("\n".join(dis(int(sys.argv[1], 16), int(sys.argv[2], 0))))
