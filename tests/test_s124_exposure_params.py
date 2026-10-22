"""Tests for S124 — el bloque de parámetros de exposición/lectura por `drive_mode`.

Tests de **bytes reales** sobre la A6000 fw3.21 y la A7S fw3.20.
"""

import pathlib
import struct

import pytest
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)


def _data(path=BIN):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _insn(data, vaddr):
    """Primera instrucción en `vaddr` (desensamblado Thumb)."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    for ins in md.disasm(data[vaddr - BASE_VADDR:vaddr - BASE_VADDR + 8], vaddr):
        return f"{ins.mnemonic} {ins.op_str}"
    return ""


class TestCamposDelBloque:
    def test_traza_de_exposicion_de_la_a6000(self):
        data = _data()
        assert _cstr(data, 0x43C93CC2) == (
            "[CAM_IMAGER]: SetExps : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] "
            "[svd:%02x] [shd:%02x] [spl:%02x] [shut:%01x]"
        )

    def test_offsets_del_bloque_de_modo(self):
        """`shut` = byte +9; PrevDrv/NowDrv/NextDrv = u16 en +4/+0/+6 (leídos en 0x436d6f70)."""
        data = _data()
        assert _insn(data, 0x436D6FAA) == "ldrh r6, [r1, #4]"   # PrevDrv
        assert _insn(data, 0x436D6FAE) == "ldrh r5, [r1]"       # NowDrv
        assert _insn(data, 0x436D6FB0) == "ldrh r7, [r1, #6]"   # NextDrv
        assert _insn(data, 0x436D6FB6) == "ldrb.w sb, [r1, #9]"  # shut

    def test_contexto_offsets_de_svd_shd_spl(self):
        """svd/shd/spl = u32 del contexto en +0x178/+0x174/+0x170 (leídos en 0x436d725c-0x436d7274)."""
        data = _data()
        for addr, off in ((0x436D725C, 0x178), (0x436D726A, 0x174), (0x436D7274, 0x170)):
            txt = _insn(data, addr)
            assert txt.startswith("ldr.w"), f"{hex(addr)}: {txt!r}"
            assert f"#0x{off:x}" in txt, f"{hex(addr)}: {txt!r} no lleva {hex(off)}"


class TestParametrosCompartidos:
    """Las 5 trazas del bloque son idénticas en A6000 y A7S (texto a texto)."""

    COMUNES = [
        "ZAF img_id:%04X, shut:%d, svd:%d, shd:%d, spl:%d, epdsel:%d",
        "Imager param error shut:%d, svr_num:%d, VdNum:%d",
        "Imager svd error. shut:%d, svd:%d -> %d",
        "shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d",
    ]

    def test_las_cuatro_trazas_estan_en_ambos_firmwares(self):
        a6000 = _data()
        a7s = _data(A7S)
        for texto in self.COMUNES:
            assert texto.encode() in a6000, texto
            assert texto.encode() in a7s, texto

    def test_la_traza_nueva_del_ciclo_de_obturacion_solo_en_a6000(self):
        a6000 = _data()
        a7s = _data(A7S)
        assert b"[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d" in a6000
        assert b"zaf_now_shut_cycle" not in a7s
        # y la que se retira
        assert b"b8_shutter_limit" not in a6000
        assert b"b8_shutter_limit" in a7s

    def test_vocabulario_de_trazas_por_firmware(self):
        a6000 = _data()
        a7s = _data(A7S)
        assert b"[CAM_IMAGER]: SetExps :" in a6000
        assert b"SetExps :" not in a7s
        assert b"Exposure. [NowDriveMode:" in a7s
        assert b"Exposure. [NowDriveMode:" not in a6000


class TestShutter:
    def test_shut_no_es_un_obturador_electronico(self):
        """`shut` va con el silenciador mecanico y el contador de ciclos, no con un selector de mecanismo."""
        data = _data()
        assert b"shutter mute on/off" in data
        assert b"shutCycleCount" in data
        assert b"uc_shut_idx_num" in data
        # ninguna traza del bloque menciona un obturador electronico
        for texto in (b"shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d",
                      b"ZAF img_id:%04X, shut:%d"):
            for palabra in (b"silent", b"electronic", b"efcs", b"curtain"):
                assert palabra not in texto.lower()
