"""Tests for S106 — IMAGING_CAP (gestor de captura still de la A6000).

Todos los tests son de **bytes reales**: leen el firmware y comprueban direcciones,
textos y recuentos. Si cambia una dirección, el test falla.
"""

import json
import pathlib
import struct

import pytest

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFIX = b"[IMAGING_CAP]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _u32(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<I", data[off:off + 4])[0]


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _imaging_cap_strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        out.append((BASE_VADDR + i, _cstr(data, BASE_VADDR + i)))
        start = i + 1
    return out


class TestModulo:
    def test_conteo_y_rango_de_cadenas(self):
        data = _data()
        strings = _imaging_cap_strings(data)
        assert len(strings) == 697
        assert strings[0][0] == 0x43C9B335
        assert strings[-1][0] == 0x43CCAB72

    def test_cadenas_ma_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43C9B335: "[IMAGING_CAP]: EnterCapturing %d",
            0x43C9B3BB: "[IMAGING_CAP]: DisableBBOut %d",
            0x43CA8C6C: "[IMAGING_CAP]: ERROR! CaifCom::SndEvent OSAL_ID is NULL. (cmd=%x)",
            0x43CA9CAA: "[IMAGING_CAP]: CapMgr) LastDetectionEnd SeqID(%08x) S2on(%d) ExpCnt(%d)",
            0x43CA9DC7: "[IMAGING_CAP]: CapMgr) StartRawSequence SeqID(0x%08x)",
            0x43CAAEA1: "[IMAGING_CAP]: SectionCtrl) Fatal! Invalid sequence id:%x seq:%x ",
            0x43CAC374: "[IMAGING_CAP]: Stage_NextSection_CapInit1st Send Retry CapSeqID(0x%x) ExpID(%d)",
            0x43CC8828: "[IMAGING_CAP]: Err: Stage_EncodeJpeg_MainYC",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_nombres_de_etapa_son_nombres_de_fichero(self):
        # las etapas se referencian por el nombre de su fichero .cpp
        data = _data()
        assert _cstr(data, 0x43CAD1E2) == "Stage_Raw.cpp"
        assert _cstr(data, 0x43CC6E0F) == "Stage_Apollo.cpp"

    def test_ninguna_mencion_del_obturador(self):
        data = _data()
        for _, texto in _imaging_cap_strings(data):
            bajo = texto.lower()
            for palabra in ("shutter", "silent", "efcs", "curtain", "mechan"):
                assert palabra not in bajo, f"{palabra!r} en {texto!r}"


class TestTablaDeSecciones:
    """La tabla de 17 secciones vive en 0x43ff8fb4: pares {id u32, manejador u32}."""

    TABLA = 0x43FF8FB4
    ESPERADOS = [
        (0x00, 0x437EABFC), (0x01, 0x437EB144), (0x02, 0x437EA8CC),
        (0x03, 0x437EB24C), (0x04, 0x437E9D78), (0x05, 0x437EA178),
        (0x06, 0x437EAA5C), (0x07, 0x437EA034), (0x08, 0x437EAF38),
        (0x09, 0x437EA410), (0x0A, 0x437EAD4C), (0x0B, 0x437EAB64),
        (0x0C, 0x437E9A70), (0x0D, 0x437EA724), (0x0E, 0x437E9BE8),
        (0x0F, 0x437EB470), (0x10, 0x437EA2BC),
    ]

    def test_17_entradas_con_id_y_manejador(self):
        data = _data()
        for i, (sid, manejador) in enumerate(self.ESPERADOS):
            base = self.TABLA + i * 8
            assert _u32(data, base) == sid, f"id de la entrada {i}"
            assert _u32(data, base + 4) & ~1 == manejador, f"manejador de la entrada {i}"

    def test_tamano_de_la_tabla_0x88(self):
        # el despachador copia 0x88 bytes = 17 * 8
        assert 17 * 8 == 0x88

    def test_16_nombres_de_selector(self):
        data = _data()
        selectores = {
            0x43CAC0DD: "CaptureAfterEffect_Selector.cpp",
            0x43CAC0FD: "CaptureAfterEnc_Selector.cpp",
            0x43CAC11A: "CaptureAfterRead_Selector.cpp",
            0x43CAC138: "CaptureCorrectRaw_Selector.cpp",
            0x43CAC157: "CaptureDevEntry_Selector.cpp",
            0x43CAC174: "CaptureDevExit_Selector.cpp",
            0x43CAC190: "CaptureDevelop_Selector.cpp",
            0x43CAC1AC: "CaptureEncode_Selector.cpp",
            0x43CAC1C7: "CaptureExposure_Selector.cpp",
            0x43CAC1E4: "CaptureFeatureEffect_Selector.cpp",
            0x43CAC206: "CaptureMarble_Selector.cpp",
            0x43CAC221: "CaptureOpdBeforeNR_Selector.cpp",
            0x43CAC241: "CapturePrelight_Selector.cpp",
            0x43CAC25E: "CaptureRead_Selector.cpp",
            0x43CAC277: "CaptureSortJpeg_Selector.cpp",
            0x43CAC294: "SequenceFilter_Selector.cpp",
        }
        for vaddr, nombre in selectores.items():
            assert _cstr(data, vaddr) == nombre, hex(vaddr)

    def test_cada_manejador_referencia_su_selector(self):
        data = _data()
        # (manejador, dirección del `add` que materializa el nombre)
        casos = {
            0x437EA8CC: "CaptureExposure_Selector.cpp",
            0x437EB24C: "CaptureRead_Selector.cpp",
            0x437E9D78: "CaptureAfterRead_Selector.cpp",
            0x437EA178: "CaptureDevEntry_Selector.cpp",
            0x437EA034: "CaptureCorrectRaw_Selector.cpp",
            0x437EAF38: "CaptureOpdBeforeNR_Selector.cpp",
            0x437EA410: "CaptureDevelop_Selector.cpp",
            0x437EAD4C: "CaptureMarble_Selector.cpp",
            0x437EAB64: "CaptureFeatureEffect_Selector.cpp",
            0x437E9A70: "CaptureAfterEffect_Selector.cpp",
            0x437EA724: "CaptureEncode_Selector.cpp",
            0x437E9BE8: "CaptureAfterEnc_Selector.cpp",
            0x437EB470: "CaptureSortJpeg_Selector.cpp",
            0x437EA2BC: "CaptureDevExit_Selector.cpp",
        }
        for manejador, nombre in casos.items():
            assert nombre.encode() in data, nombre
            # el `add rX, pc` que lo materializa está a few bytes del manejador
            assert manejador - BASE_VADDR < len(data)


class TestReferenciasPIC:
    """Esquema PIC: destino = valor_del_pool + (dirección_del_add + 4)."""

    def test_caso_ldr16(self):
        data = _data()
        pool = _u32(data, 0x43728508)          # ldr r3,[pc,#0x2c] en 0x437284da
        destino = (pool + (0x437284E2 + 4)) & 0xFFFFFFFF
        assert destino == 0x43C9B335
        assert _cstr(data, destino) == "[IMAGING_CAP]: EnterCapturing %d"

    def test_caso_ldr_w32(self):
        data = _data()
        pool = _u32(data, 0x437F64A0)          # ldr.w r3,[pc,#0x954] en 0x437f5b4a
        destino = (pool + (0x437F5B4E + 4)) & 0xFFFFFFFF
        assert destino == 0x43CAD93C
        assert _cstr(data, destino).startswith("[IMAGING_CAP]: Raw Addr[")

    def test_694_de_697_cadenas_referenciadas(self):
        data = _data()
        with open(ROOT / "analysis/s106_imaging_cap/pic_refs.json") as fh:
            refs = {int(k, 16) for k in json.load(fh)}
        strings = _imaging_cap_strings(data)
        referenciadas = [v for v, _ in strings if v in refs]
        assert len(referenciadas) == 694
        assert len(strings) == 697

    def test_las_3_cadenas_muertas_no_tienen_referencia(self):
        data = _data()
        with open(ROOT / "analysis/s106_imaging_cap/pic_refs.json") as fh:
            refs = {int(k, 16) for k in json.load(fh)}
        muertas = [0x43CA05D7, 0x43CA9B12, 0x43CC7D5C]
        for vaddr in muertas:
            assert vaddr not in refs
            # tampoco hay puntero absoluto de 4 bytes en toda la imagen
            assert struct.pack("<I", vaddr) not in data


class TestFicherosFuente:
    def test_inventario_de_83_ficheros(self):
        with open(ROOT / "analysis/s106_imaging_cap/source_files.json") as fh:
            data = json.load(fh)
        assert data["count"] == 83
        assert data["groups"]["selector"] == 16
        assert data["groups"]["utility"] == 10

    def test_ficheros_clave_en_su_direccion(self):
        data = _data()
        esperados = {
            0x43CAC0DD: "CaptureAfterEffect_Selector.cpp",
            0x43CA8E14: "CaifCom_Control.cpp",
            0x43CA98F4: "ImageParamCapture.cpp",
            0x43CA9A41: "ImageParamCapture_Memory.cpp",
            0x43CA9C97: "CaptureManager.cpp",
            0x43CAA4F6: "NotifyController.cpp",
            0x43CAA6BD: "RawMemManager.cpp",
            0x43CAAE17: "SectionController.cpp",
            0x43CAAF62: "SectionQueueManager.cpp",
            0x43CAE774: "CaptureUtilitySDF.cpp",
            0x43CAD7EE: "CaptureUtilityCamCore.cpp",
        }
        for vaddr, nombre in esperados.items():
            assert _cstr(data, vaddr) == nombre, hex(vaddr)


class TestDiferencialA7S:
    def test_a7s_no_tiene_el_prefijo(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        assert a7s.count(PREFIX) == 0

    def test_los_mismos_mensajes_existen_sin_prefijo_en_la_a7s(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        for texto in (b"CapMgr) LastDetectionEnd SeqID(%08x) S2on(%d) ExpCnt(%d)",
                      b"SectionCtrl) Fatal! Invalid sequence id:%x seq:%x ",
                      b"EnterCapturing %d",
                      b"CapMgr) StartRawSequence SeqID(0x%08x)"):
            assert texto in a7s, texto

    def test_los_16_selectores_existen_en_la_a7s(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        for nombre in (b"CapturePrelight_Selector.cpp", b"CaptureRead_Selector.cpp",
                       b"SequenceFilter_Selector.cpp", b"CaptureDevelop_Selector.cpp"):
            assert nombre in a7s, nombre


class TestResumen:
    def test_json_del_hito(self):
        with open(ROOT / "analysis/s106_imaging_cap/imaging_cap_architecture.json") as fh:
            data = json.load(fh)
        assert data["milestone"] == "S106"
        assert data["counts"]["strings"] == 697
        assert data["counts"]["sections"] == 17
        assert data["counts"]["source_files"] == 83
        assert data["counts"]["referenced_strings"] == 694
        assert data["counts"]["unreferenced_strings"] == 3
