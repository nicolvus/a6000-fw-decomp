"""Tests de S173 — `[CAM_UTIL]` (10) y `[CAMERA_ADJ]` (3): utilidades compartidas.

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
ANA = os.path.join(ROOT, "analysis/s173_cam_util_labels")
MAP = os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json")


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
# 1) Recuentos y diferencial
# --------------------------------------------------------------------------

def test_las_etiquetas_solo_existen_en_la_a6000(a6000, a7s, a6300):
    assert a6000.count(b"[CAM_UTIL]") == 10
    assert a6000.count(b"[CAMERA_ADJ]") == 3
    assert a7s.count(b"[CAM_UTIL]") == 0
    assert a7s.count(b"[CAMERA_ADJ]") == 0
    assert a6300.count(b"[CAM_UTIL]") == 0
    assert a6300.count(b"[CAMERA_ADJ]") == 0


def test_las_treze_cadenas_estan_vivas(mapa, a6000):
    """Las 13 cadenas tienen referencia PIC y ninguna está muerta."""
    n = 0
    for d in mapa:
        va = int(d, 16)
        o = va - BASE
        if o < 0 or o >= len(a6000):
            continue
        e = a6000.find(b"\x00", o)
        s = a6000[o:e]
        if s.startswith(b"[CAM_UTIL]") or s.startswith(b"[CAMERA_ADJ]"):
            assert len(mapa[d]) >= 1, s
            n += 1
    assert n == 13


# --------------------------------------------------------------------------
# 2) Direcciones y sitios concretos
# --------------------------------------------------------------------------

@pytest.mark.parametrize("addr,sitios", [
    ("0x43caaac2", ["0x437e3cb8"]),
    ("0x43caab0f", ["0x437e3d0e", "0x437e4332"]),
    ("0x43caab40", ["0x437e3dba", "0x437e446e"]),
    ("0x43ccdca9", ["0x43900254"]),
    ("0x43ccdccd", ["0x4390029a"]),
    ("0x43cce128", ["0x43900da6"]),
    ("0x43cce166", ["0x43900e8a"]),
    ("0x43cce1a7", ["0x43900f6c"]),
    ("0x43cce282", ["0x43901938"]),
    ("0x43cce2c5", ["0x43901968"]),
    ("0x43cce2f3", ["0x439019e2"]),
    ("0x43ccf20c", ["0x43904034"]),
    ("0x43ccf242", ["0x43904092"]),
])
def test_sitios_pic_de_cada_cadena(mapa, addr, sitios):
    assert mapa[addr] == [int(s, 16) for s in sitios]


def test_el_texto_de_las_cadenas_en_su_direccion(a6000):
    assert a6000.find(b"[CAM_UTIL]: AV DDS Alloc Msg Err:%x") + BASE == 0x43CCDCA9
    assert a6000.find(b"[CAMERA_ADJ]:   Utility MS UnMount Start OSAL MEM ALLOC Error : %x") + BASE == 0x43CCE1A7
    assert a6000.find(b"[CAM_UTIL]: osal_try_valloc_msg 0x%02x error! %dtimes") + BASE == 0x43CCF20C


# --------------------------------------------------------------------------
# 3) Comportamiento verificado
# --------------------------------------------------------------------------

def test_init_deja_el_id_de_modulo_0xb5(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6000[0x4390178E - BASE:0x439017E4 - BASE], 0x4390178E)]
    assert ("movs", "r2, #0xb5") in ops
    assert ("subs", "r2, #0xb0") in ops
    assert ("cmp", "r2, #0x11") in ops          # 17 entradas
    assert ("add.w", "r0, r2, #0x198") in ops   # 22 registros de 0x18 B


def test_contador_de_valloc_limpia_el_bit_de_error(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6000[0x4390400E - BASE:0x43904054 - BASE], 0x4390400E)]
    assert ("ldrb.w", "r3, [r6, #0xfc]") in ops
    assert ("tst.w", "r3, #1") in ops
    assert ("bic", "r3, r3, #1") in ops
    assert ("bl", "#0x43903f5c") in ops
    assert ("bl", "#0x43902718") in ops


def test_registro_de_tareas_compara_con_dos_entradas(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6000[0x4390199C - BASE:0x439019D0 - BASE], 0x4390199C)]
    assert ("bl", "#0x43b2a10a") in ops
    assert ("bl", "#0x43b2a116") in ops
    assert ("ldrb", "r1, [r2]") in ops
    assert ("ldrb", "r2, [r2, #1]") in ops


# --------------------------------------------------------------------------
# 4) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "cam_util_labels.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S173"
    assert j["recuentos"]["cadenas"] == 13
    assert j["recuentos"]["sitios_pic"] == 16
    assert j["recuentos"]["muertas"] == 0
    fw = j["firmwares"]
    assert fw["A6000_fw321"]["CAM_UTIL"] == 10
    assert fw["A6000_fw321"]["CAMERA_ADJ"] == 3
    assert fw["A7S_fw320"]["CAM_UTIL"] == 0
    assert fw["A6300_fw201"]["CAMERA_ADJ"] == 0
    assert len(j["cadenas"]) == 13
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]


def test_informe_del_hito():
    with open(os.path.join(ANA, "cam_util_labels.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "0x4390178e" in t and "0xb5" in t
    assert "EvtDrvnTsk" in t
