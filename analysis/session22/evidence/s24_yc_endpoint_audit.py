"""Audita estáticamente la asignación del endpoint Dataflow de Camera.YC0."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIBOBJ = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libObj.so"
)
OBJDUMP = "llvm-objdump"


def disassemble(start: int, stop: int) -> str:
    return subprocess.check_output(
        [
            OBJDUMP,
            "-d",
            "--triple=thumbv7-linux-gnueabi",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(LIBOBJ),
        ],
        text=True,
    )


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"evidencia ausente: {needle}")


def main() -> None:
    if not LIBOBJ.is_file():
        raise FileNotFoundError(LIBOBJ)

    camera_ctor = disassemble(0x987EB6, 0x987EC8)
    parser_ctor = disassemble(0xA281DC, 0xA28220)
    effect_config = disassemble(0x15D6C0, 0x15D7A6)

    for needle in (
        "movs\tr0, #0x54",
        "ldr\tr2, [r4, #0x58]",
        "bl\t0xa281dc",
        "str.w\tr5, [r4, #0xa0]",
    ):
        require(camera_ctor, needle)

    for needle in (
        "bl\t0x9581a4",
        "bl\t0x97ec80",
        "ldr\tr3, [pc, #0x18]",
        "str\tr3, [r4, #0x10]",
        "str\tr2, [r4, #0x18]",
        "str\tr2, [r4, #0x28]",
    ):
        require(parser_ctor, needle)

    for needle in (
        "DataflowInfraChC1Et",
        "DataflowInfraCh18infraDisconnectPin",
        "DataflowInfraCh11infraGetPin",
        "DataflowInfraCh15infraConnectPin",
        "ldr\tr3, [pc, #0x54]",
    ):
        require(effect_config, needle)

    raw = LIBOBJ.read_bytes()
    endpoint = (0x50004).to_bytes(4, "little")
    if raw.count(endpoint) < 6:
        raise AssertionError("endpoint 0x50004 no aparece en los sitios esperados")

    print("PASS: ObjCamera.YC0 fija endpoint Dataflow 0x50004; ObjEffect lo reconecta")


if __name__ == "__main__":
    main()
