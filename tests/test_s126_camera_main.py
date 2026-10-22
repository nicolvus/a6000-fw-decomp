"""Tests for S126 — `[CAMERA_MAIN]`, el módulo raíz de la cámara (135 trazas).

Tests de **bytes reales** sobre la A6000 fw3.21, la A7S fw3.20 y el A6300 fw2.01.
"""

import json
import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PREFIX = "[CAMERA_MAIN]"


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
    with open(ROOT / "analysis" / "s126_camera_main" / "summary.json", encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_y_rango(self):
        data = _data()
        s = _strings(data)
        assert len(s) == 135
        assert s[0][0] == 0x43C9C57B
        assert s[-1][0] == 0x43CCAE46

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43C9C57B: "[CAMERA_MAIN]: calibration_fc_pos:%d getFcPos(suc_ref_index_target):%d getFcPos(",
            0x43C9C6D5: "[CAMERA_MAIN]: Calibration start",
            0x43C9CD19: "[CAMERA_MAIN]: FOCUS MODE is not AF-A",
            0x43C9CD3F: "[CAMERA_MAIN]: Scanless NG because of Face AF",
            0x43C9CE07: "[CAMERA_MAIN]: this lens is not permitted",
            0x43C9D07E: "[CAMERA_MAIN]: NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable. lc_HybridAF.cpp %d",
            0x43C9D53F: "[CAMERA_MAIN]: waku area is %d",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr).startswith(texto), hex(vaddr)

    def test_mapa_de_funciones(self):
        s = _summary()
        assert s["counts"]["strings"] == 135
        assert s["counts"]["functions"] == 48
        assert s["counts"]["source_files"] >= 100

    def test_ficheros_fuente_de_la_capa_de_coordinacion(self):
        s = _summary()
        nombres = {f["name"] for f in s["source_files"]}
        for n in ("CamResource.cpp", "CamSyncResource.cpp", "SyncTask.cpp",
                  "ClockControl.cpp", "init_cam_SetCamParam_main.cpp", "ImagingMain.cpp"):
            assert n in nombres, n


class TestDiferencial:
    def test_la_etiqueta_es_nueva_en_la_fw321(self):
        a7s = _data(A7S)
        a6300 = _data(A6300)
        assert a7s.count(PREFIX.encode()) == 0
        assert a6300.count(PREFIX.encode()) == 0

    def test_cuenta_de_mensajes_comunes(self):
        s = _summary()
        assert s["diff"]["A7S"]["prefijo"] == 0
        assert s["diff"]["A7S"]["comunes_texto_a_texto"] == 92
        assert s["diff"]["A7S"]["solo_a6000"] == 43
        assert s["diff"]["A6300"]["comunes_texto_a_texto"] == 121
        assert s["diff"]["A6300"]["solo_a6000"] == 14

    def test_los_mismos_mensajes_existen_sin_etiqueta(self):
        a7s = _data(A7S)
        assert b"Calibration start" in a7s
        assert b"Scanless NG because of Face AF" in a7s
        assert b"waku area is %d" in a7s
