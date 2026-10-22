"""Tests for S107 — `Camera::CamCore` (37 cadenas `[CAMCORE]`) y ResourceStack.

Todos los tests son de **bytes reales**: leen el firmware y comprueban direcciones,
textos y recuentos. Si cambia una dirección, el test falla.
"""

import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
PREFIX = b"[CAMCORE]"


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


def _camcore_strings(data):
    """Retorna (vaddr, texto) de todas las cadenas [CAMCORE] en el binario."""
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        v = BASE_VADDR + i
        text = _cstr(data, v)
        out.append((v, text))
        start = i + 1
    return out


class TestModulo:
    def test_conteo_y_rango_de_cadenas(self):
        data = _data()
        strings = _camcore_strings(data)
        assert len(strings) == 37, f"Se esperaban 37 cadenas [CAMCORE], hallaron {len(strings)}"
        # Rango: primera a última
        assert strings[0][0] >= 0x43C905CA
        assert strings[-1][0] <= 0x43CEBCB2

    def test_cadenas_específicas(self):
        data = _data()
        esperados = {
            0x43C905CA: "[CAMCORE]: GetFlowType: No SgcTable. imgmode=%d, cammode=%d",
            0x43C90606: "[CAMCORE]: Warning! The controller for mode(%d) does not implemented",
            0x43C906B6: "N6Camera7CamCore8RdcImageE",
            0x43C9070A: "[CAMCORE]: SetCasRMaxRatio parameter error [%d]",
            0x43C9073A: "[CAMCORE]: typeof(rawIn) must be RdcImage.",
            0x43C90765: "[CAMCORE]: Cannot read with skipping when 4bit RAW.",
            0x43C90799: "[CAMCORE]: typeof(rawOut) must be RdcImage.",
            0x43C90846: "[CAMCORE]: [Error] Memory for PFR couldn't be freed. : unit_handle = %x",
            0x43C9088E: "[CAMCORE]: [Error] Memory for PFR couldn't be allocated.",
            0x43C908E7: "[CAMCORE]: MemoryPool has no space.",
            0x43C90982: "[CAMCORE]: SplitEEController: Memory Close Error!(VATR)",
            0x43C909BA: "[CAMCORE]: NOT SUPPORT!",
            0x43C909F7: "[CAMCORE]: No SgcTable. imgmode=%d, cammode=%d, hFlip=%u, vFlip=%u",
            0x43C90A96: "[CAMCORE]: AIF%d out[%d] > memsize[%d]",
            0x43C90ABD: "[CAMCORE]: Extent size must be just divided into equal size.",
            0x43C90AFA: "[CAMCORE]: AIF%d out[%d] memsize[%d] extent[%d]",
            0x43C90B2A: "[CAMCORE]: AIF%d Extent count[%d] must be 1 or 2.",
            0x43C90B5C: "[CAMCORE]: AIF%d pbl_aif_set_func error[%d] size[%d] dest[%d] iib[%d] addr[%08x]",
            0x43C90BAD: "[CAMCORE]: AIF%d RDC param error. encType[%d] lcut[%d] rcut[%d]",
            0x43C90BED: "[CAMCORE]: AIF%d RDC none. encType[%d] lcut[%d] rcut[%d]",
            0x43C90CA3: "[CAMCORE]: PFR in width[%d] > 596",
            0x43C90E8D: "[CAMCORE]: Interruption::AddStartCallback(%d, %08x) NG.",
            0x43C90EC5: "[CAMCORE]: ResourceBase::Release was called without acquire. %08x",
            0x43C90F07: "[CAMCORE]: MonPowersave[%d] is already Enabled !",
            0x43C90F38: "[CAMCORE]: SGC1: Invalid imager_if_type enum %d",
            0x43C90F98: "[CAMCORE]: ExlHelper: Cannot convert CamMode[%d] to ExlMode.",
            0x43C90FD5: "[CAMCORE]: ExlHelper: Invalid imager_mode_aspect[%d]",
            0x43C9100A: "[CAMCORE]: ExlHelper: Invalid imager_if_type[%d]",
            0x43C9103B: "[CAMCORE]: ExlHelper: Invalid imager_physical_coding[%d]",
            0x43C91074: "[CAMCORE]: ExlHelper: Invalid imager_aspect[%d]",
            0x43C910A4: "[CAMCORE]: [Setter] DMA Err open [%d]",
            0x43C910CA: "[CAMCORE]: [Setter] DMAC_CH_NONE",
            0x43C910EB: "[CAMCORE]: [Setter] listCount = %d",
            0x43C9110E: "[CAMCORE]: [Setter] DMA Err status [%d]",
            0x43C91136: "[CAMCORE]: [Setter] DMA Err set_func [%d]",
            0x43C91160: "[CAMCORE]: [Setter] DMA Err start [%d]",
            0x43CEBCB2: "[CAMCORE]: Acl::CAMHEAD_Z1C::setDefectPt return err.",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, f"vaddr {hex(vaddr)}: texto mismatch"


class TestResourceStack:
    """Tests de la pila ResourceStack ( dentro de [IMAGING_CAP] )."""

    RS_ADDRS = [
        0x43CA10D1,
        0x43CA110D,
        0x43CA11C2,
        0x43CA120F,
    ]

    def test_cadenas_resource_stack(self):
        data = _data()
        # Las 4 strings de ResourceStack dentro del bloque IMAGING_CAP
        expected_texts = [
            "[IMAGING_CAP]: ResourceStack)CamCore Release Error!: 0x%02x",
            "[IMAGING_CAP]: ResourceStack)rcct_Release err RC: RC_ERR:0x%02x",
            "[IMAGING_CAP]: ResourceStack)Dfe Release Error!: %02x",
            "[IMAGING_CAP]: ResStack) GetMemIndex Err handle:%x",
        ]
        for vaddr, expected in zip(self.RS_ADDRS, expected_texts):
            assert _cstr(data, vaddr) == expected, f"ResourceStack vaddr {hex(vaddr)}"

    def test_resource_stack_en_imaging_cap(self):
        data = _data()
        # Verificar que esas vaddrs caen en el bloque imaging_cap (0x43c9b335-0x43ccab72)
        for vaddr in self.RS_ADDRS:
            assert 0x43C9B335 <= vaddr <= 0x43CCAB72, f"vaddr {hex(vaddr)} fuera del bloque IMAGING_CAP"


class TestDiferencialA7S:
    def test_a7s_no_tiene_camcore(self):
        ruta = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        assert a7s.count(PREFIX) == 0

    def test_a7s_tiene_los_mismos_subsistemas_sin_etiqueta(self):
        """Correccion de la revision: ExlHelper, MonPowersave y ResourceStack) SI estan en la A7S."""
        ruta = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(ruta, "rb") as fh:
            a7s = fh.read()
        assert a7s.count(b"ExlHelper") == 5
        assert a7s.count(b"MonPowersave") == 1
        for texto in (b"ResourceStack)CamCore Release Error!: 0x%02x",
                      b"ResourceStack)FOPD Acquire Fatal Error!: %x",
                      b"ResourceStack)FOPD Release Fatal Error!: %x"):
            assert texto in a7s, texto


class TestRTTI:
    def test_rtti_camera_camcore_rdcimage(self):
        data = _data()
        assert _cstr(data, 0x43C906B6) == "N6Camera7CamCore8RdcImageE"

    def test_rtti_camera_camcore_splittdcimage(self):
        data = _data()
        # La dirección exacta del RTTI SplitRdcImage la ubicamos por rango
        # Está en 0x43cb0b94 según S104 / RTTI knowledge
        assert _cstr(data, 0x43CB0B94) == "N6Camera7CamCore13SplitRdcImageE"


class TestFicherosFuente:
    def test_json_del_hito(self):
        with open(ROOT / "analysis/s107_camcore/camcore_resources.json") as fh:
            dat = json.load(fh)
        assert dat["milestone"] == "S107"
        assert dat["count_strings"] == 37
        assert dat["base_vaddr"] == "0x43541000"