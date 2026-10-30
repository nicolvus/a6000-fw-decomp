"""R16: BossFirm (ARM7) desde bootloader.bin[0x18800:+0x3800]. Desensamblado ARM (capstone) y búsqueda de accesos. Solo lectura."""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, Cs

BL = (
    Path(__file__).resolve().parents[1]
    / "camera-dumps/updater-20261020-175427/bootloader.bin"
)
OFF, LEN = 0x18800, 14336
IMG = BL.read_bytes()[OFF : OFF + LEN]
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)


def sha() -> str:
    return hashlib.sha256(IMG).hexdigest()


def dis(a: int, n: int) -> list[str]:
    return [
        f"{i.address:05x}: {i.mnemonic} {i.op_str}"
        for i in MD.disasm(IMG[a : a + n], a)
    ]


def lit(a: int) -> int:
    return struct.unpack_from("<I", IMG, a)[0]


if __name__ == "__main__":
    if sys.argv[1] == "sha":
        print(sha())
    else:
        print("\n".join(dis(int(sys.argv[1], 16), int(sys.argv[2], 0))))
