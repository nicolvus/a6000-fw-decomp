"""Audita estáticamente el puente Dataflow usado por los parsers YC de Camera."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIBOBJ = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libObj.so"
)
OBJDUMP = "llvm-objdump"


def disassemble(start: int, stop: int) -> str:
    """Devuelve sólo el rango Thumb solicitado del ELF original."""
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
    """Hace fallar la auditoría cuando una prueba estática deja de coincidir."""
    if needle not in text:
        raise AssertionError(f"evidencia ausente: {needle}")


def main() -> None:
    if not LIBOBJ.is_file():
        raise FileNotFoundError(LIBOBJ)

    parser = disassemble(0xA27B22, 0xA27C44)
    transport = disassemble(0xA14F88, 0xA15110)
    helpers = disassemble(0x143428, 0x143470)

    for needle in (
        "movw\tr1, #0x1001",
        "movw\tr1, #0x1002",
        "movw\tr1, #0x1003",
        "str\tr0, [r4, #0x34]",
        "str\tr0, [r4, #0x38]",
        "str\tr0, [r4, #0x3c]",
        "str\tr0, [r4, #0x40]",
        "bl\t0xa14f88",
    ):
        require(parser, needle)

    for needle in (
        "DataflowInfraMsg14SetDataflowMsgEPvt",
        "DataflowInfraMsg10SetReplyIdEj",
        "DataflowInfraMsg8SetSrcIdEj",
        "DataflowInfraSender9SendASyncEjP16DataflowInfraMsg",
        "DataflowInfraReceiver12ReceiveASyncEjP16DataflowInfraMsgm",
        "mov.w\tr3, #0xffffffff",
        "movs\tr2, #0x14",
        "cmp\tr5, #0x1",
    ):
        require(transport, needle)

    for needle in (
        "mov.w\tr1, #0x1000",
        "movs\tr1, #0x14",
        "movs\tr1, #0x2",
        "str\tr1, [r0, #0x8]",
        "str\tr1, [r0, #0xc]",
    ):
        require(helpers, needle)

    digest = hashlib.sha256(LIBOBJ.read_bytes()).hexdigest()
    print(f"PASS: puente YC/Dataflow verificado para libObj.so sha256={digest}")


if __name__ == "__main__":
    main()
