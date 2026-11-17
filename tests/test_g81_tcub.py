"""G81 — Timecode / User Bit: piezas de fábrica en libObj, libmpr y av-cam 3.21 (bytes reales)."""
from pathlib import Path

import capstone
import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
pytestmark = pytest.mark.skipif(not (LIB / "libObj.so").exists(), reason="extracción no disponible")


def _txt(d, a, b):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[a:b], a)]


def test_emisores_de_ui_y_comprobacion_de_inhibicion():
    """UI 0x6005dc…0x600b04: ObjMsg(0x3900, 0x3016…0x301b) a Effect; ObjEffect 0xbc4c06 consulta GetInhInfo(0x34b) (y 0x36c para 0x3018) antes de aceptarlo."""
    d = (LIB / "libObj.so").read_bytes()
    t = _txt(d, 0x6005DC, 0x600C00)
    for m in ("0x3016", "0x3017", "0x3018", "0x3019", "0x301a", "0x301b"):
        assert any(x.endswith(f"#{m}") for x in t), m
    c = _txt(d, 0xBC4C0E, 0xBC4C24)
    assert c[0] == "movw r0, #0x34b" and "movw r3, #0x3018" in c and "mov.w r0, #0x36c" in c
    assert b"[ObjEffect]tcub(msgId:0x%x) is Inhbited" in d or b"is Inhbited" in d


def test_escritura_y_generacion_tcub():
    assert b"b_timeCodeEnable" in (LIB / "libmpr.so").read_bytes()
    if AVCAM.exists():
        a = AVCAM.read_bytes()
        assert b"McTcubIf" in a and b"NotifyEncodeTcubInfo" in a and b"VdfSrvcCmdSetTimeCode" in a
