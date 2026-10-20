"""Audita seis microprocesos estáticos de Camera.YC0 sin ejecutar firmware."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIBOBJ = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libObj.so"
)
LIBBIZ = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib/libBizFw.so"
)
OBJDUMP = "llvm-objdump"


def disassemble(binary: Path, start: int, stop: int) -> str:
    """Devuelve un intervalo Thumb del ELF original, sin modificarlo."""
    return subprocess.check_output(
        [
            OBJDUMP,
            "-d",
            "--triple=thumbv7-linux-gnueabi",
            f"--start-address=0x{start:x}",
            f"--stop-address=0x{stop:x}",
            str(binary),
        ],
        text=True,
    )


def require(text: str, *needles: str) -> None:
    """Exige todas las huellas ensamblador/símbolo de un microproceso."""
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"evidencia ausente: {needle}")


def main() -> None:
    if not LIBOBJ.is_file() or not LIBBIZ.is_file():
        raise FileNotFoundError("faltan ELF originales requeridos")

    lifecycle = disassemble(LIBOBJ, 0x987EB6, 0x987EC8)
    admission = disassemble(LIBOBJ, 0xA27B22, 0xA27C06)
    serialization = disassemble(LIBOBJ, 0x143428, 0x143470)
    transport = disassemble(LIBOBJ, 0xA14F88, 0xA15110)
    registry = disassemble(LIBBIZ, 0x35A74, 0x35BA4)
    relay = disassemble(LIBOBJ, 0xA279E8, 0xA27F42)

    require(lifecycle, "movs\tr0, #0x54", "ldr\tr2, [r4, #0x58]", "bl\t0xa281dc", "str.w\tr5, [r4, #0xa0]")
    require(admission, "movw\tr1, #0x1001", "movw\tr1, #0x1002", "movw\tr1, #0x1003", "str\tr0, [r4, #0x34]", "str\tr0, [r4, #0x40]")
    require(serialization, "mov.w\tr1, #0x1000", "movs\tr1, #0x14", "movs\tr1, #0x2", "str\tr1, [r0, #0x8]", "str\tr1, [r0, #0xc]")
    require(transport, "DataflowInfraMsg14SetDataflowMsgEPvt", "DataflowInfraMsg10SetReplyIdEj", "DataflowInfraMsg8SetSrcIdEj", "DataflowInfraSender9SendASyncEjP16DataflowInfraMsg", "DataflowInfraReceiver12ReceiveASyncEjP16DataflowInfraMsgm", "mov.w\tr3, #0xffffffff", "cmp\tr5, #0x1")
    require(registry, "_MSG_PIN_GETC1Ev", "mov.w\tr3, #0x1000", "DataflowInfraCh22sndRcvAsyncDataflowMsg", "str\tr6, [r4, #0x1c]")
    require(relay, "_ZN3MWF6ObjMsgC1Ejj@plt", "_ZN3MWF6ObjMsg20CopyCommonRelayParamEPKS0_@plt", "movw\tr3, #0x1003", "_ZN3MWF6ObjPin4SendEjPNS_6ObjMsgE@plt")

    print("PASS: seis microprocesos Camera.YC0/Dataflow cerrados en su alcance estático")


if __name__ == "__main__":
    main()
