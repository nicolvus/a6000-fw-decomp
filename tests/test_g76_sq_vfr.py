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
    """CamMsgConv::SetOUCrankModeForLiro: MSGID 0x75e4/0x75e6 → orden 0x408f con PARAMID_O_U_CRANK_MODE 0x971a (byte 8) y _FRAME_RATE 0x971b (0x207…0x20d, 0x3e2 → 0…7 en el byte 9); 0x9724 es de la orden 0x4087."""
    d = (LIB / "libObj.so").read_bytes()
    txt = {f"{m} {o}" for _, m, o in _ins(d, 0x99F140, 0x99F2A0)} | {f"{m} {o}" for _, m, o in _ins(d, 0x99F18C, 0x99F1C0)}
    for need in ("movw r3, #0x75e4", "movw r3, #0x75e6", "movw r1, #0x9724", "movw r1, #0x971b", "movw r3, #0x3e2", "strb r3, [r4, #9]"):
        assert need in txt, need


@pytest.mark.skipif(not (LIB / "CautionConfig.so").exists(), reason="extracción no disponible")
def test_sin_menu_s_q_en_la_a6000():
    """No hay nodos de menú de S&Q/cámara lenta en CautionConfig: la función existe por debajo pero no se puede pedir desde la UI."""
    d = (LIB / "CautionConfig.so").read_bytes().lower()
    assert all(k not in d for k in (b"slowquick", b"slow_quick", b"crank", b"s&q"))


@pytest.mark.skipif(not (LIB / "libObj.so").exists(), reason="extracción no disponible")
def test_s_q_a_120_pide_el_formato_hfr():
    """SeqSetOUCrankMode (`0xa1aa90`) arma `0x408f` y una orden EE `0x4000` de 0x17 B; con VALUEID_O_U_CRANK_FR_120_100 (`0x3e2`) pone su byte 0xd = 4,
    la misma clase de formato 4 de «120p» (G70: el selector de av-cam `0x4380e43c` elige con ella el modo de sensor 0x12 a 120 Hz)."""
    d = (LIB / "libObj.so").read_bytes()
    txt = [f"{m} {o}" for _, m, o in _ins(d, 0xA1AAD8, 0xA1AADC)] + [f"{m} {o}" for _, m, o in _ins(d, 0xA1AD0C, 0xA1AD28)]
    assert txt[0] == "movw r0, #0x408f"
    assert txt[1:] == ["mov.w r0, #0x4000", "add.w r1, r7, #0x28", "adds r2, r7, #4", "ldr r3, [r4, #0x10]", "bl #0x9bbb5c",
                       "movw r3, #0x3e2", "cmp r8, r3", "bne #0xa1ad28", "movs r3, #4", "strb r3, [r7, #0xd]"]


def _busca(d, entrada, fr, sr, activo=1):
    """Ejecuta (Unicorn, av-cam real) la búsqueda O/U Crank desde `entrada` con el objeto de vídeo {+0xc+0x104 activo, +0x105 sR, +0x108 fR}."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(0x43000000, 0x1100000)
    mu.mem_write(B, d)
    mu.mem_map(0x10000000, 0x20000)
    obj = 0x10000000
    o = obj + 0xC
    mu.mem_write(o + 0x104, bytes([activo, sr]))
    mu.mem_write(o + 0x108, struct.pack("<I", fr))
    fin = 0x10010000

    def stub(uc, addr, size, _):  # registro de av-cam (0x435b3040 contexto, 0x43a4e4e8 printf): sin efecto en el resultado
        if addr in (0x435B3040, 0x43A4E4E8):
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    mu.hook_add(UC_HOOK_CODE, stub)
    mu.reg_write(UC_ARM_REG_SP, 0x1001F000)
    mu.reg_write(UC_ARM_REG_LR, fin | 1)
    mu.reg_write(UC_ARM_REG_R0, obj)
    mu.emu_start(entrada | 1, fin, count=200_000)
    return mu.reg_read(UC_ARM_REG_R0)


@pytest.mark.skipif(not AVCAM.exists(), reason="av-cam.bin no disponible")
def test_parche_s_q_120_amplia_la_tabla_sin_cambiar_lo_de_fabrica():
    """VFR-F4: con el parche, (fR 24/30/60p, 120 fps) y (25/50p, 100 fps) son válidas; lo de fábrica (60 fps, 1 fps) y lo inválido (7 fps,
    S&Q apagado) dan lo mismo que sin parche. Sin parche 120/100 caen en «OuCrank Config Err» (0)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sq120", ROOT / "scripts/g76/sq120_patch.py")
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    d = AVCAM.read_bytes()
    p = P.patch(d)
    assert P.patch(p) == p
    assert sum(a != b for a, b in zip(d, p, strict=True)) <= 4 + 0x60 + 8 * len(P.FILAS)
    for fr, sr in P.FILAS:
        assert _busca(d, P.BUSCA, fr, sr) == 0
        assert _busca(p, P.CUEVA, fr, sr) == 1
    for fr, sr, activo in ((4, 60, 1), (2, 1, 1), (5, 50, 1), (4, 7, 1), (4, 120, 0), (7, 120, 1)):
        assert _busca(p, P.CUEVA, fr, sr, activo) == _busca(d, P.BUSCA, fr, sr, activo), (fr, sr, activo)
