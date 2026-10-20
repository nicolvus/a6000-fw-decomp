"""Audita la resolución de pines Dataflow sin ejecutar el firmware."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIBBIZ = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libBizFw.so"
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
            str(LIBBIZ),
        ],
        text=True,
    )


def require(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"evidencia ausente: {needle}")


def main() -> None:
    if not LIBBIZ.is_file():
        raise FileNotFoundError(LIBBIZ)

    get_pin = disassemble(0x35A74, 0x35BA4)
    for needle in (
        "_MSG_PIN_GETC1Ev",
        "mov.w\tr3, #0x1000",
        "_MSG_PIN_GET_COMPC1Ev",
        "DataflowInfraCh22sndRcvAsyncDataflowMsg",
        "str\tr6, [r4, #0x1c]",
    ):
        require(get_pin, needle)

    print(
        "PASS: infraGetPin consulta el registro Dataflow y copia el pin desde "
        "una respuesta, no desde una tabla endpoint→callback local"
    )


if __name__ == "__main__":
    main()
