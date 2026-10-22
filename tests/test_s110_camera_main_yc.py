"""Tests for S110 — `Camera::YC` (motor de imagen, `[CAMERA_MAIN_YC]`).

Todos los tests son de **bytes reales**: leen el firmware y comprueban direcciones,
textos y recuentos. Si cambia una dirección, el test falla.
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
PREFIX = "[CAMERA_MAIN_YC]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=240):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _yc_strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        out.append((BASE_VADDR + i, _cstr(data, BASE_VADDR + i)))
        start = i + 1
    return out


def _json(name):
    with open(ROOT / "analysis" / "s110_camera_main_yc" / name, encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_y_rango(self):
        data = _data()
        strings = _yc_strings(data)
        assert len(strings) == 970
        assert strings[0][0] == 0x43CA88F6
        assert strings[-1][0] == 0x43CCD469

    def test_cuatro_bloques(self):
        bl = _json("blocks.json")["blocks"]
        assert len(bl) == 4
        assert [(b["lo"], b["hi"], b["n"]) for b in bl] == [
            ("0x43ca88f6", "0x43ca8c49", 17),
            ("0x43cb79ea", "0x43cbe577", 430),
            ("0x43cbf241", "0x43cc56af", 361),
            ("0x43ccb48e", "0x43ccd469", 162),
        ]

    def test_cadenas_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CA88F6: "[CAMERA_MAIN_YC]: ---api_YC_CaptureRawReadExecuteClp---",
            0x43CB7CDB: None,     # inicio del bloque MARBLE (se comprueba aparte)
            0x43CBC27C: "[CAMERA_MAIN_YC]: HD_SWEEP_HOLD  =%x",
            0x43CC4FF9: "[CAMERA_MAIN_YC]: YAP: job_apc_main_stl main_digitalZoomRatioDenom=%x",
            0x43CC50FB: "[CAMERA_MAIN_YC]: YAP: job_apc_main_mov digitalZoomRatioDenom=%x",
        }
        for vaddr, texto in esperados.items():
            if texto is None:
                continue
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_api_y_jobs_renombrados(self):
        data = _data()
        for nombre in ("api_YC_InitCap", "api_YC_SetCapBoks", "api_YC_SetCapStar",
                       "api_YC_SetCapTbox", "api_YC_SetSaCamDsp", "api_YC_SetVdPreParam",
                       "api_YC_LfnrSetParam", "api_YC_DEV_SetCoodinate"):
            assert nombre.encode() in data, nombre
        for nombre in ("job_YC_Initialize", "job_YC_ModeManager", "job_YC_SetParam",
                       "job_YC_SetParamOn", "job_YC_SetParamOff", "job_YC_SetParamPrelight",
                       "job_YC_SetPreParam", "job_YC_SetSaCamDspParam", "job_YC_CalcParam",
                       "job_YC_SetCapBoks", "job_YC_SetCapStar", "job_YC_GetTagPointer"):
            assert nombre.encode() in data, nombre


class TestMapaDeFunciones:
    def test_970_cadenas_en_332_funciones(self):
        fm = _json("func_map.json")
        assert fm["n_functions"] == 332
        assert fm["sin_funcion"] == 0
        # cada cadena puede referenciarse desde varias funciones: se cuentan las
        # cadenas distintas cubiertas por el mapa (960 de 970; las 10 restantes
        # no tienen ninguna referencia en la imagen)
        unicas = {s["vaddr"] for f in fm["functions"] for s in f["strings"]}
        assert len(unicas) == 960
        assert sum(f["n_strings"] for f in fm["functions"]) == 2295

    def test_diez_cadenas_sin_referencia(self):
        """Las 10 cadenas sin referencia: ni PIC ni puntero absoluto de 4 B."""
        fm = _json("func_map.json")
        unicas = {s["vaddr"] for f in fm["functions"] for s in f["strings"]}
        rows = _json("strings_raw.json")["strings"]
        sin_ref = sorted(r["vaddr"] for r in rows if r["vaddr"] not in unicas)
        assert sin_ref == ["0x43ca88f6", "0x43ca8af8", "0x43cbb0e4", "0x43cbe537",
                           "0x43cc3d9c", "0x43cc435b", "0x43cc5340", "0x43ccd278",
                           "0x43ccd2ec", "0x43ccd439"]
        data = _data()
        for vaddr in sin_ref:
            assert struct.pack("<I", int(vaddr, 16)) not in data, vaddr

    def test_atribucion_cruzada_con_s78(self):
        """El metodo PIC+prologos reproduce las direcciones que S78 obtuvo con Ghidra."""
        fm = _json("func_map.json")
        por_func = {f["func"]: f for f in fm["functions"]}
        assert "0x438b3ea8" in por_func          # job_apc_main_stl (S78)
        assert "0x438b5810" in por_func          # job_apc_main_mov (S78)
        textos = {s["text"] for s in por_func["0x438b3ea8"]["strings"]}
        assert any("job_apc_main_stl" in t for t in textos)
        textos = {s["text"] for s in por_func["0x438b5810"]["strings"]}
        assert any("job_apc_main_mov" in t for t in textos)

    def test_api_con_su_funcion(self):
        fm = _json("func_map.json")
        por_func = {f["func"]: f for f in fm["functions"]}
        assert any("api_YC_InitCap" in s["text"]
                   for s in por_func["0x437cf5f0"]["strings"])
        assert any("api_YC_SetCapBoks" in s["text"]
                   for s in por_func["0x437d8c88"]["strings"])


class TestSubmodulos:
    def test_principales_submodulos(self):
        s = _json("yc_summary.json")
        por = {x["submodule"]: x for x in s["submodules"]}
        for nombre, n in (("SHD", 219), ("ITP", 90), ("YAP", 79), ("DCV", 42),
                          ("OLC", 37), ("NR", 36), ("CLP", 29), ("MARBLE", 24),
                          ("KKNR", 22), ("PFR", 19)):
            assert por[nombre]["n"] == n, nombre
        assert s["counts"]["submodules"] == 141

    def test_8_api_y_12_jobs(self):
        s = _json("yc_summary.json")
        assert len(s["api_yc"]) == 8
        assert len(s["job_yc"]) == 12


class TestFicherosFuente:
    def test_inventario_de_119_ficheros(self):
        files = _json("source_files.json")["files"]
        assert len(files) == 119
        nombres = {f["name"] for f in files}
        for n in ("Sequence_Common.cpp", "Sequence_Movie.cpp", "yc_clp_common.cpp",
                  "init_cam_SetCamParam.cpp", "SyncLoader.cpp", "CS_ExifMakerNote.cpp",
                  "ddl_stitch.cpp", "Stage_MARBLE.cpp"):
            assert n in nombres, n

    def test_ficheros_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CB14A1: "Sequence_Common.cpp",
            0x43CB31F1: "Sequence_Movie.cpp",
            0x43CB81AC: "yc_clp_common.cpp",
            0x43CB40B8: "init_cam_SetCamParam.cpp",
            0x43CB397A: "SyncLoader.cpp",
            0x43CC56DC: "CS_ExifMakerNote.cpp",
            0x43CC6964: "ddl_stitch.cpp",
        }
        for vaddr, nombre in esperados.items():
            assert _cstr(data, vaddr) == nombre, hex(vaddr)


class TestDiferencialA7S:
    def test_a7s_no_tiene_el_prefijo(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        assert a7s.count(PREFIX.encode()) == 0

    def test_969_de_970_comunes_y_una_nueva(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        data = _data()
        comunes = 0
        solo = []
        for vaddr, texto in _yc_strings(data):
            core = texto[len(PREFIX) + 2:] if texto.startswith(PREFIX + ": ") else texto
            if core.encode() in a7s:
                comunes += 1
            else:
                solo.append((vaddr, core))
        assert comunes == 969
        assert solo == [(0x43CBC27C, "HD_SWEEP_HOLD  =%x")]

    def test_mismos_mensajes_sin_etiqueta_en_la_a7s(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        for texto in (b"YAP:\tjob_YC_RawDevMakerNote_Yap_apc_init",
                      b"MARBLE: MOV\t<MBL_MOV_Image_Mod> ul_rc_zo"):
            assert texto in a7s, texto
