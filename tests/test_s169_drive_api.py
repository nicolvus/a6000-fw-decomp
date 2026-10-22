"""Tests de S169 — control positivo del obturador electrónico: API de drive del A6300.

Tests de **bytes reales**: si cambia una dirección, un texto o un contador, fallan.

Convención del repo: `vaddr = 0x43541000 + file_offset` (válido para los tres firmwares).
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
ANA = os.path.join(ROOT, "analysis/s169_drive_api")


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
def pares():
    with open(os.path.join(ANA, "checkset_pairs.json"), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# 1) Diferencial de la familia CheckSet*
# --------------------------------------------------------------------------

def test_checkset_esta_ausente_en_a6000_y_a7s(a6000, a7s):
    assert a6000.count(b"CheckSet") == 0
    assert a7s.count(b"CheckSet") == 0


def test_checkset_esta_presente_en_a6300(a6300):
    n = a6300.count(b"CheckSet")
    assert n >= 201


def test_paramcheckerr_ausente_en_a6000_y_a7s(a6000, a7s):
    assert a6000.count(b"ParamCheckErr") == 0
    assert a7s.count(b"ParamCheckErr") == 0
    assert a6300_paramcheckerr_count() == 370


def a6300_paramcheckerr_count():
    with open(A6300, "rb") as fh:
        return fh.read().count(b"ParamCheckErr")


@pytest.mark.parametrize("campo", [
    b"sc_ShutDrive", b"uc_ShutDriveMode", b"front_eshutter", b"SilentShutterMode",
    b"shutterType", b"sc_IrisDrive", b"uc_IrisDriveMode", b"sc_ExposureDrive",
    b"ul_ShutLowLimit", b"isoAutoMinShutSpeedMode", b"MovieAutoSlowshutMode",
])
def test_campos_de_obturador_solo_en_a6300(a6000, a7s, a6300, campo):
    assert a6000.count(campo) == 0
    assert a7s.count(campo) == 0
    assert a6300.count(campo) >= 1


def test_liro_seq_existe_en_las_tres_pero_solo_el_a6300_tiene_paramcheck(a6000, a7s, a6300):
    assert a6000.count(b"LiroSeq") == 2
    assert a7s.count(b"LiroSeq") == 2
    assert a6300.count(b"LiroSeq") >= 370


def test_drive_mode_del_imager_sigue_presente_en_la_a6000(a6000):
    """El 'drive_mode' de S134 (imager) NO es lo mismo que 'sc_ShutDrive'."""
    assert a6000.count(b"drive_mode") == 10
    assert a6000.count(b"sc_ShutDrive") == 0


# --------------------------------------------------------------------------
# 2) Pares propiedad <-> campo, y sus direcciones
# --------------------------------------------------------------------------

def _par(pares, propiedad, campo):
    for p in pares["pares"]:
        if p["propiedad"] == propiedad and p["campo"] == campo:
            return p
    return None


def test_hay_387_pares(pares):
    assert pares["n"] == 387


@pytest.mark.parametrize("prop,campo,sitio,offset", [
    ("CheckSetShutDrive", "sc_ShutDrive", "438c51c0", "0x1dd"),
    ("CheckSetShutDriveMode", "uc_ShutDriveMode", "438c6842", "0x1dc"),
    ("CheckSetFrontEshutter", "front_eshutter", "438c6e1e", "0x23c"),
    ("CheckSetSilentShutterMode", "SilentShutterMode", "438c81da", "0x264"),
    ("CheckSetShutterType", "shutterType", "438c8b52", "0x268"),
    ("CheckSetIrisDrive", "sc_IrisDrive", "438c55a2", "0x1d1"),
    ("CheckSetIrisDriveMode", "uc_IrisDriveMode", "438c680e", "0x1d0"),
])
def test_pares_de_obturador_con_direcciones(pares, prop, campo, sitio, offset):
    p = _par(pares, prop, campo)
    assert p is not None, f"falta el par {prop}/{campo}"
    assert p["sitio_add_etiqueta"] == sitio
    assert p["offset_campo"] == offset
    assert "ParamCheckErr" in p["mensaje"]
    assert campo in p["mensaje"]


def test_los_201_nombres_checkset_estan_todos_vivos(a6300):
    """Cada etiqueta CheckSet* referenciada tiene al menos un sitio PIC en el mapa."""
    with open(os.path.join(ANA, "pic_refs_strict_a6300.json"), encoding="utf-8") as fh:
        mapa = json.load(fh)
    B = a6300
    n = 0
    for dest in mapa:
        va = int(dest, 16)
        o = va - BASE
        if o < 0 or o >= len(B):
            continue
        e = B.find(b"\x00", o)
        if B[o:e].startswith(b"CheckSet"):
            assert len(mapa[dest]) >= 1, dest
            n += 1
    assert n == 201


# --------------------------------------------------------------------------
# 3) Bytes concretos de los sitios verificados a mano
# --------------------------------------------------------------------------

def _dis(blob, va, n=1):
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    return list(md.disasm(blob[va - BASE:va - BASE + n * 4], va))


def test_codigo_del_check_de_sc_shutdrive(a6300):
    """0x438c51ae: ldrsb.w r2,[r0,#0x1dd] ; ... ; add r0,pc ; add r1,pc ; b.w 0x43986518"""
    ins = _dis(a6300, 0x438C51AE, 2)
    assert ins[0].mnemonic == "ldrsb.w"
    assert ins[0].op_str == "r2, [r0, #0x1dd]"
    # el par de 'add' y la rama al logger
    adds = _dis(a6300, 0x438C51BE, 2)
    assert (adds[0].mnemonic, adds[0].op_str) == ("add", "r0, pc")
    assert (adds[1].mnemonic, adds[1].op_str) == ("add", "r1, pc")
    branch = _dis(a6300, 0x438C51C6, 1)[0]
    assert branch.mnemonic == "b.w"
    assert branch.op_str == "#0x43986518"


def test_pool_de_los_dos_add_en_sc_shutdrive(a6300):
    """Los pools de 0x438c51ba/0x438c51bc dan mensaje y etiqueta (destino = pool + add + 4)."""
    def tgt(ldr_va, add_va):
        h = struct.unpack("<H", a6300[ldr_va - BASE:ldr_va - BASE + 2])[0]
        assert (h & 0xF800) == 0x4800
        pool = ((ldr_va + 4) & ~3) + ((h & 0xFF) * 4)
        w = struct.unpack("<I", a6300[pool - BASE:pool - BASE + 4])[0]
        return (w + add_va + 4) & 0xFFFFFFFF
    msg = tgt(0x438C51BA, 0x438C51BE)
    lab = tgt(0x438C51BC, 0x438C51C0)
    assert b"LiroSeq ParamCheckErr" in a6300[msg - BASE:msg - BASE + 80]
    assert b"sc_ShutDrive" in a6300[msg - BASE:msg - BASE + 80]
    assert a6300[lab - BASE:lab - BASE + 17] == b"CheckSetShutDrive"


def test_codigo_del_check_de_front_eshutter(a6300):
    ins = _dis(a6300, 0x438C6E0E, 1)[0]
    assert ins.mnemonic == "ldr.w"
    assert ins.op_str == "r2, [r0, #0x23c]"


def test_codigo_del_check_de_silentshuttermode(a6300):
    ins = _dis(a6300, 0x438C81CA, 1)[0]
    assert ins.mnemonic == "ldr.w"
    assert ins.op_str == "r2, [r0, #0x264]"


# --------------------------------------------------------------------------
# 4) Datos estructurados y mapas
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "drive_api.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S169"
    t = j["firmwares"]
    for k in ("A6000_fw321", "A7S_fw320"):
        assert t[k]["terminos"]["CheckSet"] == 0
        assert t[k]["terminos"]["ParamCheckErr"] == 0
        assert t[k]["terminos"]["sc_ShutDrive"] == 0
        assert t[k]["terminos"]["front_eshutter"] == 0
        assert t[k]["terminos"]["SilentShutterMode"] == 0
        assert t[k]["terminos"]["shutterType"] == 0
    a = t["A6300_fw201"]["terminos"]
    assert a["CheckSet"] >= 201
    assert a["ParamCheckErr"] == 370
    assert a["sc_ShutDrive"] == 1
    assert a["front_eshutter"] == 1
    assert a["shutterType"] == 1
    assert j["capas_liro_seq"]["pares_propiedad_campo"] == 387
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]


def test_mapas_pic_de_los_tres_firmwares():
    with open(os.path.join(ANA, "pic_refs_strict_a6300.json"), encoding="utf-8") as fh:
        m6300 = json.load(fh)
    with open(os.path.join(ANA, "pic_refs_strict_a7s.json"), encoding="utf-8") as fh:
        m7 = json.load(fh)
    with open(os.path.join(ROOT, "analysis/s106_imaging_cap/pic_refs_strict_global.json"),
              encoding="utf-8") as fh:
        m6 = json.load(fh)
    assert len(m6300) == 20001
    assert len(m7) == 16638
    assert len(m6) == 17525


def test_informe_del_hito():
    with open(os.path.join(ANA, "drive_api.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "sc_ShutDrive" in t and "front_eshutter" in t
    assert "0x438c51c0" in t
    assert "S51" in t
