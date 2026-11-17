"""G76 — Variable Frame Rate = S&Q (O/U Crank) de Sony: piezas de fábrica en av-cam y libObj 3.21 (bytes reales)."""
import struct
from pathlib import Path

import capstone
import pytest

ROOT = Path(__file__).resolve().parents[1]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
B = 0x43541000
TABLA = 0x43B93BF4  # copiada (0x1c8 B) por 0x435d709c, que busca (fR, sR) y registra «[O/U Crank] Table[%d] fR sR»


@pytest.mark.skipif(not AVCAM.exists(), reason="av-cam.bin no disponible")
def test_tabla_o_u_crank_de_av_cam():
    """57 filas {u32 fR, u8 sR, u8 válido}: NTSC fR 4/2/6 con captura 60…1 fps, PAL fR 5/3 con 50…1, y 7–10 solo a 1 fps."""
    d = AVCAM.read_bytes()
    filas = [(struct.unpack_from("<I", d, TABLA - B + 8 * k)[0], d[TABLA - B + 8 * k + 4], d[TABLA - B + 8 * k + 5]) for k in range(57)]
    ntsc, pal = [60, 30, 20, 16, 12, 10, 8, 6, 4, 2, 1], [50, 24, 16, 12, 10, 8, 6, 4, 2, 1]
    esperado = [(fr, s, 1) for fr in (4, 2, 6) for s in ntsc] + [(fr, s, 1) for fr in (5, 3) for s in pal] + [(fr, 1, 1) for fr in (7, 8, 9, 10)]
    assert filas == esperado


def _ins(d, a, b):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return [(i.address, i.mnemonic, i.op_str) for i in md.disasm(d[a:b], a)]


@pytest.mark.skipif(not (LIB / "libObj.so").exists(), reason="extracción no disponible")
def test_libobj_convierte_s_q_para_av_cam():
    """CamMsgConv::SetOUCrankModeForLiro: MSGID 0x75e4/0x75e6, PARAMID_O_U_CRANK_MODE 0x9724 y _FRAME_RATE 0x971b (0x207…0x20d, 0x3e2 → 0…7 en el byte 9)."""
    d = (LIB / "libObj.so").read_bytes()
    txt = {f"{m} {o}" for _, m, o in _ins(d, 0x99F140, 0x99F2A0)} | {f"{m} {o}" for _, m, o in _ins(d, 0x99F18C, 0x99F1C0)}
    for need in ("movw r3, #0x75e4", "movw r3, #0x75e6", "movw r1, #0x9724", "movw r1, #0x971b", "movw r3, #0x3e2", "strb r3, [r4, #9]"):
        assert need in txt, need


@pytest.mark.skipif(not (LIB / "CautionConfig.so").exists(), reason="extracción no disponible")
def test_sin_menu_s_q_en_la_a6000():
    """No hay nodos de menú de S&Q/cámara lenta en CautionConfig: la función existe por debajo pero no se puede pedir desde la UI."""
    d = (LIB / "CautionConfig.so").read_bytes().lower()
    assert all(k not in d for k in (b"slowquick", b"slow_quick", b"crank", b"s&q"))
