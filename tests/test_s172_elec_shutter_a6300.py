"""Tests de S172 — el módulo `ElecShutter` del A6300: qué hace realmente.

Tests de **bytes reales**: si cambia una dirección, un texto o un contador, fallan.
"""
import json
import os
import struct

import pytest

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A6000 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                           "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
ANA = os.path.join(ROOT, "analysis/s172_elec_shutter_a6300")
MAP = os.path.join(ROOT, "analysis/s169_drive_api/pic_refs_strict_a6300.json")


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def a6000():
    return _read(A6000)


@pytest.fixture(scope="module")
def a7s():
    return _read(A7S)


@pytest.fixture(scope="module")
def a6300():
    return _read(A6300)


@pytest.fixture(scope="module")
def mapa():
    with open(MAP, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# 1) Las cadenas de __FILE__ solo existen en el A6300
# --------------------------------------------------------------------------

@pytest.mark.parametrize("s", [
    "ElecShutter/EC_ElecShutter_Main.cpp",
    "ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp",
])
def test_las_cadenas_de_file_solo_estan_en_a6300(a6000, a7s, a6300, s):
    assert a6000.count(s.encode()) == 0
    assert a7s.count(s.encode()) == 0
    assert a6300.count(s.encode()) == 1


def test_direcciones_de_las_cadenas(a6300):
    assert a6300.find(b"ElecShutter/EC_ElecShutter_Main.cpp") + BASE == 0x43DCFA41
    assert a6300.find(b"ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp") + BASE == 0x43DCFA65
    assert a6300.find(b"EC_ASSERT %s:%d") + BASE == 0x43DB1A4D


@pytest.mark.parametrize("addr,sitios", [
    ("0x43dcfa41", ["0x4391d6a2"]),
    ("0x43dcfa65", ["0x4391dd50", "0x4391ddb0"]),
])
def test_sitios_pic_de_las_cadenas_de_file(mapa, addr, sitios):
    assert mapa[addr] == [int(s, 16) for s in sitios]


# --------------------------------------------------------------------------
# 2) La función de código de modo de obturador
# --------------------------------------------------------------------------

def test_codigos_de_modo_0x80_y_0x100(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ins = list(md.disasm(a6300[0x4391D67C - BASE:0x4391D6B8 - BASE], 0x4391D67C))
    ops = [(i.mnemonic, i.op_str) for i in ins]
    assert ("cmp", "r3, #0x80") in ops
    assert ("cmp.w", "r3, #0x100") in ops
    assert ("movs", "r0, #3") in ops
    assert ("movs", "r0, #4") in ops
    assert ("ldrh", "r3, [r3]") in ops


def test_linea_de_assert_0x421_en_el_main(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ins = list(md.disasm(a6300[0x4391D698 - BASE:0x4391D6A8 - BASE], 0x4391D698))
    ops = [(i.mnemonic, i.op_str) for i in ins]
    assert ("movw", "r2, #0x421") in ops
    assert ("bl", "#0x43986518") in ops


def test_el_formato_ec_assert_no_existe_en_la_a6000(a6000, a7s, a6300):
    """El formato 'EC_ASSERT %s:%d' es 0/1/1; lo del A6300 son los ficheros ElecShutter/."""
    assert a6000.count(b"EC_ASSERT %s:%d") == 0
    assert a7s.count(b"EC_ASSERT %s:%d") == 1
    assert a6300.count(b"EC_ASSERT %s:%d") == 1


def test_lineas_de_assert_0x23c_y_0x24f_en_la_tabla(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for va, linea in ((0x4391DD46, "r2, #0x23c"), (0x4391DDA6, "r2, #0x24f")):
        ins = list(md.disasm(a6300[va - BASE:va + 8 - BASE], va))
        ops = [(i.mnemonic, i.op_str) for i in ins]
        assert ("mov.w" if ops[1][0] == "mov.w" else "movw", linea) in ops


# --------------------------------------------------------------------------
# 3) La tabla no lineal
# --------------------------------------------------------------------------

def test_escalas_de_la_tabla_no_lineal(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6300[0x4391DC00 - BASE:0x4391DCD0 - BASE], 0x4391DC00)]
    assert ("mov.w", "r2, #0x3e8") in ops          # escala 1000
    assert ("movw", "r0, #0x2710") in ops          # escala 10000
    # lectura de la fila: 32 bits por fila
    assert any(mn.startswith("ldr.w") and "[r2, r6, lsl #2]" in op for mn, op in ops)


def test_busqueda_en_punto_fijo_16_16(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6300[0x4391DD34 - BASE:0x4391DD78 - BASE], 0x4391DD34)]
    assert ("movs", "r2, #0xf") in ops            # 15 bits fraccionarios
    assert ("mov.w", "r3, #0x8000") in ops         # escala 32768
    assert any(mn.startswith("lsl.w") and "lr, lr, r2" in op for mn, op in ops)


# --------------------------------------------------------------------------
# 4) Corrección a S135: el bloque de 128 bytes no está referenciado
# --------------------------------------------------------------------------

def test_el_bloque_de_128_bytes_no_tiene_referencias(mapa, a6300):
    clave = "0x43dcfa9e"
    assert clave not in mapa, "el bloque no deberia tener referencias PIC"
    pat = struct.pack("<I", 0x43DCFA9E)
    assert a6300.count(pat) == 0, "no deberia haber punteros absolutos"


def test_el_bloque_es_una_tabla_byte_a_byte_no_decreciente(a6300):
    off = 0x43DCFA9E - BASE
    tab = a6300[off:off + 128]
    assert len(tab) == 128
    assert list(tab[:4]) == [0, 1, 3, 4]
    assert tab == bytes(sorted(tab)), "deberia ser no decreciente"
    # valores repetidos (indicio de tabla de caracteres)
    assert tab.count(0x54) == 2 and tab.count(0x60) == 2 and tab.count(0x7F) == 2


# --------------------------------------------------------------------------
# 5) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "elec_shutter_a6300.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S172"
    fw = j["firmwares"]
    for k in ("A6000_fw321", "A7S_fw320"):
        assert fw[k]["terminos"]["ElecShutter/EC_ElecShutter_Main.cpp"] == 0
        assert fw[k]["terminos"]["ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp"] == 0
        assert fw[k]["terminos"]["EC_ASSERT %s:%d"] == (0 if k == "A6000_fw321" else 1)
    a = fw["A6300_fw201"]["terminos"]
    assert a["ElecShutter/EC_ElecShutter_Main.cpp"] == 1
    assert a["ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp"] == 1
    assert a["EC_ASSERT %s:%d"] == 1
    assert j["funcion_modo_obturador"]["codigos"] == {"0x80": 3, "0x100": 4}
    assert "NO esta verificada" in j["correccion_a_s135"]["conclusion"]
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]


def test_informe_del_hito():
    with open(os.path.join(ANA, "elec_shutter_a6300.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "0x43dcfa9e" in t and "0x4391d67c" in t
    assert "S135" in t and "corrección" in t.lower()
