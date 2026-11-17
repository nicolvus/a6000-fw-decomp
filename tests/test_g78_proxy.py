"""G78 — Dual Video Recording = grabación proxy de Sony: piezas de fábrica en libObj y av-cam 3.21 (bytes reales)."""
from pathlib import Path

import capstone
import pytest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so"
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"


def _txt(d, a, b, base=0):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[a - base:b - base], a)]


@pytest.mark.skipif(not LIB.exists(), reason="libObj.so no disponible")
def test_emisor_de_ui_pone_proxy_segun_el_global():
    """0x5ffb20 arma MSGID_SET_MOVIE_FORMAT_CMD (0x750e); PARAMID_MOVIE_PROXY (0x99bd) = ON 0x498 si el byte global (GOT+0x4810 → 0x10ab200) ≠ 0, si no OFF 0x499.
    El global lo pone a 1 0x5f8ec6 en los modelos model/MOVIE_REC_MANUAL_PROXY y model/MOVIE_REC_MULTI_CTRL_PROXY."""
    d = LIB.read_bytes()
    t = _txt(d, 0x5FFD10, 0x5FFD3C)
    assert t[:7] == ["ldr r3, [pc, #0x3d8]", "ldr.w r3, [r8, r3]", "ldrb.w fp, [r3]", "movw r3, #0x499", "cmp.w fp, #0", "ite eq", "moveq fp, r3"]
    assert "movne.w fp, #0x498" in t and "movw r1, #0x99bd" in t
    assert b"model/MOVIE_REC_MANUAL_PROXY\0" in d and b"model/MOVIE_REC_MULTI_CTRL_PROXY\0" in d
    assert _txt(d, 0x5F8EC6, 0x5F8ECA) == ["movs r3, #1", "strb r3, [r5]"]


@pytest.mark.skipif(not LIB.exists(), reason="libObj.so no disponible")
def test_conversor_lleva_el_proxy_a_la_orden_0x4000():
    """CamMsgConv 0x9b6ad4: 0x750e → orden LIRO 0x4000; 0x99bd (proxy) → byte 0xe, 0x99be → 0xf, 0x99bf → 0x10, 0x99c0 → 0x11, 0x99c1 → 0x12, 0x99c2 → 0x13, 0x99c3 → 0x14."""
    d = LIB.read_bytes()
    t = _txt(d, 0x9B6AD4, 0x9B72EC)
    for pid, byte in ((0x99BD, 0xE), (0x99BE, 0xF), (0x99BF, 0x10), (0x99C0, 0x11), (0x99C1, 0x12), (0x99C2, 0x13), (0x99C3, 0x14)):
        assert f"movw r1, #{pid:#x}" in t and f"strb r3, [r4, #{byte:#x}]" in t
    assert "movw r3, #0x750e" in t
    assert _txt(d, 0x9B7336, 0x9B733E) == ["movs r3, #0x40", "strb.w r8, [r4, #4]", "strb r3, [r4, #3]"]


@pytest.mark.skipif(not AVCAM.exists(), reason="av-cam.bin no disponible")
def test_av_cam_tiene_ruta_proxy():
    d = AVCAM.read_bytes()
    assert b"PROXY PIN_OUT_STATE is not READY" in d and b"ActEnc_2nd" in d
