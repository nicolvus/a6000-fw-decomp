"""E26-R19 — pruebas offline de la capa USB de darwin_core.bin (FM3). Se omiten si falta el binario.

Comprueban bytes y literales del desensamblado; no demuestran comportamiento del USB Charger real.
"""

import hashlib
import struct
from pathlib import Path

import pytest

BIN = (
    Path(__file__).resolve().parents[1]
    / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)
pytestmark = pytest.mark.skipif(not BIN.exists(), reason="darwin_core.bin ausente")


@pytest.fixture(scope="module")
def d():
    data = BIN.read_bytes()
    assert hashlib.sha256(data).hexdigest().startswith("5f2be06d")
    return data


def word(d, a):
    return struct.unpack_from("<I", d, a)[0]


def test_callbacks_usb_registrados(d):
    # 0xc650: cuatro punteros apilados y pasados a la inicialización USB 0x19284
    assert [word(d, a) for a in (0xC778, 0xC77C, 0xC780, 0xC784)] == [
        0x1079D,
        0x1077F,
        0x10717,
        0x106C1,
    ]


def test_despacho_clase_vendor_al_callback(d):
    # 0xd032: ldr r1,[=0x200032a4]; ldr r1,[r1]; cbz; bx r1
    assert 0x200032A4 in {word(d, a) for a in range(0xD070, 0xD090, 4)}
    assert d[0x19388:0x1938A] == bytes.fromhex("4178")  # ldrb r1,[r0,#1] (bRequest)


def test_sin_flash_if_ni_literal_mfs_en_codigo(d):
    for a in range(0, 0x23000, 4):
        w = word(d, a)
        assert not 0x40000000 <= w < 0x40003000 or (a >= 0x21000), hex(a)


def test_tabla_dwn_22_rutinas_sin_flash_ni_referencias(d):
    t = [(word(d, 0x21950 + 4 * i) & ~1) - 0x4200 for i in range(22)]
    assert d[0x21938:0x21943] == b"DWN_VER0.78" and word(d, 0x21950 + 4 * 22) == 0
    assert 0x2F50 == min(t) and 0x4BA8 == max(t)
    assert not any(
        abs(word(d, a) - (0x21950 + 0x4200)) <= 0x20 for a in range(0, 0x21000, 4)
    )


def test_mapeo_base_0x4200(d):
    # descriptor de dispositivo USB: archivo 0x239e4 = dirección 0x27be4 (puntero en 0x23a40)
    assert (
        d[0x239E4:0x239E8].hex() == "12010002" and word(d, 0x23A40) == 0x239E4 + 0x4200
    )
