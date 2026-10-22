"""Tests de S171 — la API del imager y el canal «SteadyShot» del objetivo.

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
ANA = os.path.join(ROOT, "analysis/s171_imager_api")


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


# --------------------------------------------------------------------------
# 1) Diferencial de la API del imager
# --------------------------------------------------------------------------

def test_la_api_del_imager_tiene_4_entradas_en_a6000_y_a7s(a6000, a7s):
    for b in (a6000, a7s):
        assert b.count(b"GetImagerDriveMode") == 1
        assert b.count(b"GetImagerTemperature") >= 1
        assert b.count(b"GetImagerTemperatureAD") == 1
        assert b.count(b"GetPrelightImagerDriveMode") == 1
        assert b.count(b"GetImagerStabilizationTime") == 0
        assert b.count(b"SetImagerFrameSize") == 0
        assert b.count(b"SetImagerMode") == 0


def test_la_api_del_imager_tiene_7_entradas_en_a6300(a6300):
    assert a6300.count(b"GetImagerDriveMode") == 1
    assert a6300.count(b"GetPrelightImagerDriveMode") == 1
    assert a6300.count(b"GetImagerStabilizationTime") == 1
    # SetImagerFrameSize aparece en la traza 'SetImagerFrameSize[%d]' y dentro de
    # 'CheckSetImagerFrameSize'; SetImagerMode, en una firma C++.
    assert a6300.count(b"SetImagerFrameSize[%d]") == 1
    assert a6300.count(b"CheckSetImagerFrameSize") == 1
    assert a6300.count(b"Camera::Sync::SyncUtilityUpm::SetImagerMode") == 1


def test_la_clase_syncutilityupm_es_exclusiva_del_a6300(a6000, a7s, a6300):
    assert a6300.count(b"SyncUtilityUpm") == 3
    assert a6300.count(b"IMAGER_DRIVEMODE") == 2
    assert a6000.count(b"SyncUtilityUpm") == 0
    assert a7s.count(b"SyncUtilityUpm") == 0
    assert a6000.count(b"IMAGER_DRIVEMODE") == 0
    assert a7s.count(b"IMAGER_DRIVEMODE") == 0


def test_steadyshot_solo_en_a6300(a6000, a7s, a6300):
    assert a6000.count(b"SteadyShot") == 0
    assert a7s.count(b"SteadyShot") == 0
    assert a6300.count(b"SteadyShot") == 11


def test_steadyshotinfo_solo_en_a6300(a6000, a7s, a6300):
    assert a6000.count(b"SteadyShotInfo") == 0
    assert a7s.count(b"SteadyShotInfo") == 0
    assert a6300.count(b"SteadyShotInfo") == 7


def test_el_modulo_mount_dividedinfo_existe_en_los_tres(a6000, a7s, a6300):
    """Lo exclusivo del A6300 es la variante SteadyShotInfo, no el driver de la montura."""
    assert a6000.count(b"Mount_DividedInfo") == 5
    assert a7s.count(b"Mount_DividedInfo") == 3
    assert a6300.count(b"Mount_DividedInfo") == 5


# --------------------------------------------------------------------------
# 2) Bytes concretos de GetImagerStabilizationTime
# --------------------------------------------------------------------------

def test_cadena_get_imager_stabilization_time_en_su_direccion(a6300):
    s = b"GetImagerStabilizationTime Request Error"
    off = a6300.find(s)
    assert off >= 0
    assert BASE + off == 0x43D9CE7F
    assert a6300[off - 1] == 0x00


def test_pool_y_sitio_de_la_referencia(a6300):
    w = struct.unpack("<I", a6300[0x43718D14 - BASE:0x43718D18 - BASE])[0]
    assert w == 0x00684177
    assert (w + 0x43718D04 + 4) & 0xFFFFFFFF == 0x43D9CE7F
    assert struct.unpack("<H", a6300[0x43718D02 - BASE:0x43718D04 - BASE])[0] == 0x4804  # ldr r0,[pc,#0x10]
    assert struct.unpack("<H", a6300[0x43718D04 - BASE:0x43718D06 - BASE])[0] == 0x4478  # add r0,pc


def test_manejador_calcula_una_suma_de_bytes(a6300):
    """count en +0x258, byte de la tabla en +0x25a, devuelve (suma+2)&0xFF."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ins = list(md.disasm(a6300[0x43718CDE - BASE:0x43718D12 - BASE], 0x43718CDE))
    ops = [(i.mnemonic, i.op_str) for i in ins]
    assert ("ldrb.w", "r4, [r3, #0x258]") in ops
    assert ("ldrb.w", "r5, [r5, #0x25a]") in ops
    assert ("adds", "r2, #2") in ops
    assert ("uxtb", "r0, r2") in ops


def test_el_error_se_registra_con_el_logger_43986518(a6300):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    ins = list(md.disasm(a6300[0x43718D02 - BASE:0x43718D0A - BASE], 0x43718D02))
    assert ins[-1].mnemonic == "bl"
    assert ins[-1].op_str == "#0x43986518"


# --------------------------------------------------------------------------
# 3) Las 7 cadenas del canal SteadyShotInfo y sus sitios
# --------------------------------------------------------------------------

@pytest.mark.parametrize("addr,sitio", [
    ("0x43da45b1", "0x4374eb60"),
    ("0x43da460a", "0x4374ec40"),
    ("0x43da4653", "0x4374ec5c"),
    ("0x43da46aa", "0x4374ecf2"),
    ("0x43da46f9", "0x4374ed44"),
    ("0x43da477b", "0x4374ed5e"),
    ("0x43da47c4", "0x4374ed6c"),
])
def test_cadenas_steadyshotinfo_vivas_con_su_sitio(a6300, addr, sitio):
    with open(os.path.join(ROOT, "analysis/s169_drive_api/pic_refs_strict_a6300.json"),
              encoding="utf-8") as fh:
        mapa = json.load(fh)
    va = int(addr, 16)
    clave = f"0x{va:x}"
    assert clave in mapa, f"{clave} no esta en el mapa"
    assert mapa[clave] == [int(sitio, 16)]
    o = va - BASE
    assert b"SteadyShot" in a6300[o:o + 80]


def test_las_cadenas_de_liro_seq_steadyshot_son_de_s169(a6300):
    for s in (b"CheckSetFrameLockOnSteadyShot", b"CheckSetSteadyShotAdvancedStill",
              b"CheckSetS1SteadyShotMode", b"CheckSetSteadyShotAdvancedMovie"):
        assert a6300.count(s) == 1


# --------------------------------------------------------------------------
# 4) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "imager_api.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S171"
    fw = j["firmwares"]
    assert fw["A6000_fw321"]["SteadyShot"] == 0
    assert fw["A7S_fw320"]["SteadyShot"] == 0
    assert fw["A6300_fw201"]["SteadyShot"] == 11
    assert fw["A6000_fw321"]["SteadyShotInfo"] == 0
    assert fw["A6300_fw201"]["SteadyShotInfo"] == 7
    assert len(fw["A6000_fw321"]["api_imager"]) == 4
    assert len(fw["A7S_fw320"]["api_imager"]) == 4
    assert len(fw["A6300_fw201"]["api_imager"]) == 7
    assert fw["A6000_fw321"]["SyncUtilityUpm"] == 0
    assert fw["A7S_fw320"]["SyncUtilityUpm"] == 0
    assert fw["A6300_fw201"]["SyncUtilityUpm"] == 3
    assert fw["A6000_fw321"]["IMAGER_DRIVEMODE"] == 0
    assert fw["A6300_fw201"]["IMAGER_DRIVEMODE"] == 2
    assert j["api_imager_solo_a6300"] == ["GetImagerStabilizationTime",
                                          "SetImagerFrameSize", "SetImagerMode"]
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]


def test_informe_del_hito():
    with open(os.path.join(ANA, "imager_api.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "GetImagerStabilizationTime" in t
    assert "SteadyShotInfo" in t
    assert "0x43718d04" in t
    assert "S51" in t
