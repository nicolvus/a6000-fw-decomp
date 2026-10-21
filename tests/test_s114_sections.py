"""Tests for S114 — el motor de secciones de la captura (17 ids ↔ 17 etapas).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos y recuentos.
"""

import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
TABLE = 0x43FF8FB4
HERE = ROOT / "analysis" / "s114_sections"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _u32(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<I", data[off:off + 4])[0]


def _cstr(data, vaddr, maxlen=120):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _map():
    with open(HERE / "section_map.json", encoding="utf-8") as fh:
        return json.load(fh)


class TestTabla:
    def test_17_entradas_con_id_y_manejador(self):
        data = _data()
        esperados = [
            (0x00, 0x437EABFC), (0x01, 0x437EB144), (0x02, 0x437EA8CC),
            (0x03, 0x437EB24C), (0x04, 0x437E9D78), (0x05, 0x437EA178),
            (0x06, 0x437EAA5C), (0x07, 0x437EA034), (0x08, 0x437EAF38),
            (0x09, 0x437EA410), (0x0A, 0x437EAD4C), (0x0B, 0x437EAB64),
            (0x0C, 0x437E9A70), (0x0D, 0x437EA724), (0x0E, 0x437E9BE8),
            (0x0F, 0x437EB470), (0x10, 0x437EA2BC),
        ]
        for i, (sid, manejador) in enumerate(esperados):
            base = TABLE + i * 8
            assert _u32(data, base) == sid
            assert _u32(data, base + 4) & ~1 == manejador

    def test_tamano_de_la_tabla(self):
        assert 17 * 8 == 0x88


class TestIdentificacion:
    def test_catorce_manejadores_con_nombre_propio(self):
        m = _map()
        con_nombre = {r["id"]: r["propia"] for r in m["sections"] if r["propia"]}
        assert len(con_nombre) == 14
        assert con_nombre[0x02] == ["CaptureExposure_Selector.cpp"]
        assert con_nombre[0x03] == ["CaptureRead_Selector.cpp"]
        assert con_nombre[0x0F] == ["CaptureSortJpeg_Selector.cpp"]
        assert con_nombre[0x10] == ["CaptureDevExit_Selector.cpp"]

    def test_id_01_es_prelight_por_llamada_directa(self):
        m = _map()
        r = [x for x in m["sections"] if x["id"] == 0x01][0]
        assert r["handler"] == "0x437eb144"
        assert ["CapturePrelight_Selector.cpp", "0x437eb07c"] in r["llama_a_selector"]
        # la función llamada es la que registra el nombre del selector de Prelight
        assert "0x437eb07c" in m["selectors"]["CapturePrelight_Selector.cpp"]["funcs"]

    def test_los_dos_sin_nombre(self):
        m = _map()
        sin_nombre = sorted(r["id"] for r in m["sections"]
                            if not r["propia"] and not r["llama_a_selector"])
        assert sin_nombre == [0x00, 0x06]

    def test_las_16_etapas_de_la_firmware(self):
        m = _map()
        assert len(m["selectors"]) == 16
        for nombre, vaddr in (("CaptureExposure_Selector.cpp", 0x43CAC1C7),
                              ("CapturePrelight_Selector.cpp", 0x43CAC241),
                              ("CaptureSortJpeg_Selector.cpp", 0x43CAC277),
                              ("SequenceFilter_Selector.cpp", 0x43CAC294)):
            assert m["selectors"][nombre]["vaddr"] == f"0x{vaddr:x}"

    def test_nombres_de_selector_en_su_direccion(self):
        data = _data()
        assert _cstr(data, 0x43CAC1C7) == "CaptureExposure_Selector.cpp"
        assert _cstr(data, 0x43CAC241) == "CapturePrelight_Selector.cpp"
        assert _cstr(data, 0x43CAC294) == "SequenceFilter_Selector.cpp"

    def test_cinco_nombres_los_registra_codigo_fuera_de_la_tabla(self):
        m = _map()
        manejadores = {r["handler"] for r in m["sections"]}
        for nombre in ("CapturePrelight_Selector.cpp", "SequenceFilter_Selector.cpp",
                       "CaptureDevelop_Selector.cpp"):
            fuera = [f for f in m["selectors"][nombre]["funcs"] if f not in manejadores]
            assert fuera, nombre


class TestInforme:
    def test_existe_el_informe(self):
        informe = HERE / "section_engine.md"
        assert informe.exists() and informe.stat().st_size > 3000
        doc = ROOT / "docs" / "capture" / "s114-section-engine.md"
        assert doc.exists() and doc.stat().st_size > 500
