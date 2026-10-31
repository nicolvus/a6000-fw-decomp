"""E26-R32: valor real de `MODEREG` registrado por Loader3 en el backup de la cámara (IDs `0x3e0003/9/a`)."""

import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "analysis/s55")
from bk4 import BK4

DUMPS = sorted(Path("analysis/camera-dumps").glob("*/backup*.bin"))
TEMPLATE = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/0110_backup/"
    "SYSMUSASHI-DSLR/DM_UUD3/CX77500_E38.bin"
)
ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin")
LOADER = Path("analysis/camera-dumps/updater-20261020-175427/bootloader.bin")


def u16(b: BK4, id_: int) -> int:
    assert b.entry(id_)[0] == 2  # entrada de 2 bytes: se guarda la mitad baja
    return struct.unpack_from("<H", b.d, b.ptr(id_))[0]


@pytest.mark.skipif(not DUMPS, reason="sin volcados de backup")
def test_backup_de_la_camara_registra_moderreg_0x0003():
    for f in DUMPS:
        b = BK4(f)
        assert u16(b, 0x3E0003) == 0x0500, f  # TYPEID & 0xff00 = TYPEID_CXD90014
        assert u16(b, 0x3E0009) == 0x0010, f
        assert u16(b, 0x3E000A) == 0x0003, f  # MODEREG[15:0]: bit0 = bit1 = 1


@pytest.mark.skipif(not TEMPLATE.exists(), reason="plantilla 0110_backup ausente")
def test_plantilla_de_fabrica_no_trae_esos_valores():
    b = BK4(TEMPLATE)
    assert (u16(b, 0x3E0003), u16(b, 0x3E000A)) == (0x00FF, 0x0000)


def test_loader3_registra_moderreg_al_final_de_su_init():
    d = LOADER.read_bytes()
    base = 0xC01F0000 - 0x22800
    assert d[0xC01F11E4 - base : 0xC01F11E8 - base] == bytes.fromhex(
        "03f088fe"
    )  # bl 0xc01f4ef8
    assert d[0x27710:0x27712] == bytes.fromhex("3e20")  # movs r0,#0x3e
    assert struct.unpack_from("<I", d, 0x2776C)[0] == 0x003E0003  # id base; +6, +7
    assert b"LD3:read MISCREG" in d


def test_bootrom_con_bit0_1_y_clave_arranca_tras_la_ventana_serie():
    """bit0=1 -> 0x10de; clave presente (0x39c != 1) -> 0x876; 0x3001 (sin sincronismo) -> 0x1226 carga y salto."""
    h = lambda a: struct.unpack_from("<H", ROM.read_bytes(), a - 0xFFFF0000)[0]
    assert (h(0xFFFF10A0), h(0xFFFF1134), h(0xFFFF1136)) == (0xD11D, 0x2801, 0xD10D)
    assert (h(0xFFFF116C), h(0xFFFF116E), h(0xFFFF1178)) == (0x4284, 0xD104, 0xE055)
