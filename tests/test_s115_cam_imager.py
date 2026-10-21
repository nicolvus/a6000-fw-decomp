"""Tests for S115 — `[CAM_IMAGER]` (driver del imager en la cámara).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos y recuentos.
"""

import json
import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PREFIX = "[CAM_IMAGER]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        end = i
        while end < len(data) and data[end] != 0:
            end += 1
        out.append((BASE_VADDR + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


def _summary():
    with open(ROOT / "analysis" / "s115_cam_imager" / "summary.json", encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_de_trazas(self):
        data = _data()
        assert len(_strings(data)) == 371

    def test_79_de_las_trazas_son_del_zit(self):
        data = _data()
        zit = [t for _, t in _strings(data) if re.match(re.escape(PREFIX) + r": (!)?ZIT", t)]
        assert len(zit) == 79

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43C931D6: "[CAM_IMAGER]: P2SData[Page:%01x] %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x %02x",
            0x43C9327C: "[CAM_IMAGER]: P2S CheckAddrOrder: ORDER ERROR !",
            0x43C939B5: "[CAM_IMAGER]: SetExpsZ: [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [svrz:%02x] [shrz:%02x] [splz:%02x] [epd:%02d] [epdsel:%02d]",
            0x43C93CC2: "[CAM_IMAGER]: SetExps : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [svd:%02x] [shd:%02x] [spl:%02x] [shut:%01x]",
            0x43C93FCB: "[CAM_IMAGER]: SetRead : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [AGainCont_EC:%02x] [AGainCont:%02x] [AGainDrv:%02x]",
            0x43C94076: "[CAM_IMAGER]: Execute : [PrevDrv:%2d] [NowDrv:%2d] [NextDrv:%2d] [SSBRK_ON:%01x] [SLEEP_ON:%01x]",
            0x43C93AE2: "[CAM_IMAGER]: Execute0:pre%02dnow%02dnext%02d ssb%01x read%dz%d svr%02dz%02d",
            0x43C94E55: "[CAM_IMAGER]: SIF SetSyncCode : Serial Synccode Not Selected",
            0x43C94E92: "[CAM_IMAGER]: SIF SetSyncCode : Parallel Synccode Not Selected",
            0x43C94617: "[CAM_IMAGER]: ImagerCommon::MacroPowerOnRequest Unknown index number",
            0x43C953E7: "[CAM_IMAGER]: SubLVDS PowerOn: SUBLCNTL_DFE1 does not exist on Regulus.",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_el_campo_shut_esta_en_la_trava_de_exposicion(self):
        """El campo `shut` aparece en la traza de SetExposicion (punto de contacto con el obturador)."""
        data = _data()
        assert "[shut:%01x]" in _cstr(data, 0x43C93CC2)

    def test_imagercommon_es_de_un_solo_canal(self):
        data = _data()
        textos = [t for _, t in _strings(data) if "ImagerCommon" in t]
        assert len(textos) == 16
        con_ch1 = [t for t in textos if "do not use CH_1" in t]
        # 8 metodos con el aviso de canal + 7 con "Unknown index number" + 1 de SIF
        assert len(con_ch1) == 8
        assert len([t for t in textos if "Unknown index number" in t]) == 7
        assert len([t for t in textos if "unknown SIF block" in t]) == 1


class TestFunciones:
    def test_94_funciones(self):
        s = _summary()
        assert s["counts"]["functions"] == 94
        assert s["counts"]["strings"] == 371

    def test_handlers_de_interrupcion(self):
        s = _summary()
        assert "int_p2s_handler" in s["interrupt_handlers"]
        assert "int_timer_handler" in s["interrupt_handlers"]

    def test_canales_p2s(self):
        s = _summary()
        assert "DFE0" in s["p2s_channels"]
        assert "DFE1" in s["p2s_channels"]


class TestDiferencialA7S:
    def test_a7s_no_tiene_el_prefijo(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        assert a7s.count(PREFIX.encode()) == 0
        # el mismo driver sí está, pero sin esas trazas concretas
        assert a7s.count(b"SetExps") == 0
        assert a7s.count(b"Execute0") == 0
        assert a7s.count(b"AGainCont") == 0
        # y el vocabulario común sí existe
        for tok in (b"P2S", b"SubLVDS", b"ImagerCommon", b"SIFSyncCode", b"SSBRK"):
            assert a7s.count(tok) > 0, tok
