"""Tests de S175 — el módulo `[LIF_DEBUG]` (13 trazas): el sensor de luz de la cámara.

Tests de **bytes reales**: si cambia una dirección, un texto o un contador, fallan.
"""
import json
import os
import re
import struct

import pytest

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A6000 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                           "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
ANA = os.path.join(ROOT, "analysis/s175_lif_debug")
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

def test_el_token_solo_existe_en_la_a6000(a6000, a7s, a6300):
    assert a6000.count(b"[LIF_DEBUG]") == 13
    assert a7s.count(b"[LIF_DEBUG]") == 0
    assert a6300.count(b"[LIF_DEBUG]") == 0


def test_el_subsistema_existe_en_los_tres_firmware(a6000, a7s, a6300):
    """Lo propio de la A6000 es la ETIQUETA, no el subsistema."""
    for b in (a6000, a7s, a6300):
        assert b.count(b"LIF") > 0
        assert b.count(b"BKID") > 0
        assert b.count(b"SENSER") > 0


def test_los_dos_nombres_de_funcion_solo_estan_en_la_a6000(a6000, a7s, a6300):
    assert a6000.count(b"cam_lif_senser_copy_bk2shadow") == 1
    assert a6000.count(b"cam_lif_senser_copy_shadow2bk") == 1
    assert a7s.count(b"cam_lif_senser_copy_bk2shadow") == 0
    assert a6300.count(b"cam_lif_senser_copy_bk2shadow") == 0


# --------------------------------------------------------------------------
# 2) Direcciones y sitios
# --------------------------------------------------------------------------

def test_rango_de_las_cadenas(a6000):
    ms = list(re.finditer(rb"\[LIF_DEBUG\][\x20-\x7e]*", a6000))
    assert len(ms) == 13
    assert BASE + ms[0].start() == 0x43CFB032
    assert BASE + ms[-1].start() == 0x43CFB224
    assert a6000[ms[0].start():ms[0].start() + 26] == b"[LIF_DEBUG]: Finish BK CB "
    assert a6000[ms[-1].start():ms[-1].start() + 43] == b"[LIF_DEBUG]: CAM LIF Subsystem backup close"


def test_las_trece_cadenas_estan_vivas(mapa, a6000):
    n = 0
    for d in mapa:
        va = int(d, 16)
        o = va - BASE
        if o < 0 or o >= len(a6000):
            continue
        e = a6000.find(b"\x00", o)
        if a6000[o:e].startswith(b"[LIF_DEBUG]"):
            assert len(mapa[d]) >= 1
            n += 1
    assert n == 13


def test_un_canal_tiene_dos_sitios(mapa, a6000):
    """'::[Count]:%x' se emite desde dos funciones distintas."""
    d = "0x43cfb0d1"
    assert d in mapa
    assert len(mapa[d]) == 2


# --------------------------------------------------------------------------
# 3) El logger propio con id 0x125
# --------------------------------------------------------------------------

def test_el_logger_propio_usa_el_id_0x125(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6000[0x43A1C92C - BASE:0x43A1C990 - BASE], 0x43A1C92C)]
    assert ("movs", "r2, #0x9a") in ops
    assert ("bl", "#0x435612d0") in ops
    assert ("blx", "#0x439c5a04") in ops
    assert ("bl", "#0x43561244") in ops


def test_las_llamadas_al_logger_pasan_el_id_0x125(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops = [(i.mnemonic, i.op_str)
           for i in md.disasm(a6000[0x43A1C9E8 - BASE:0x43A1CA10 - BASE], 0x43A1C9E8)]
    assert ("movw", "r0, #0x125") in ops
    assert ("movs", "r2, #3") in ops


def test_las_copias_shadow_recorren_dos_elementos(a6000):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ops1 = [(i.mnemonic, i.op_str)
            for i in md.disasm(a6000[0x43A1CA36 - BASE:0x43A1CAB0 - BASE], 0x43A1CA36)]
    ops2 = [(i.mnemonic, i.op_str)
            for i in md.disasm(a6000[0x43A1CB52 - BASE:0x43A1CBA0 - BASE], 0x43A1CB52)]
    assert ("cmp", "r7, #2") in ops1
    assert ("cmp", "r4, #2") in ops2


# --------------------------------------------------------------------------
# 4) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "lif_debug.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S175"
    assert j["recuentos"]["cadenas"] == 13
    assert j["recuentos"]["sitios_pic"] == 14
    assert j["recuentos"]["muertas"] == 0
    assert j["firmwares"]["A6000_fw321"]["LIF_DEBUG"] == 13
    assert j["firmwares"]["A7S_fw320"]["LIF_DEBUG"] == 0
    assert j["firmwares"]["A6300_fw201"]["LIF_DEBUG"] == 0
    assert len(j["cadenas"]) == 13
    assert j["logger"]["id_categoria"] == "0x125"
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]


def test_informe_del_hito():
    with open(os.path.join(ANA, "lif_debug.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "0x43a1c92c" in t and "0x125" in t
    assert "cam_lif_senser_copy_bk2shadow" in t
