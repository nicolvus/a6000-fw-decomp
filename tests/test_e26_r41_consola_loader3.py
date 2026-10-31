"""E26-R41 — Consola serie de Loader3 (`beast`/`ldump`) y espera de ICE.

Leen `bootloader.bin` y los volcados BK4; se omiten si faltan.  Nada toca la cámara.
"""

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "analysis" / "e26-recovery")]

BL = ROOT / "analysis/camera-dumps/updater-20261020-175427/bootloader.bin"
L3, OFF3 = 0xC01F0000, 0x22800
L2, OFF2 = 0xC0030000, 0x600


def _l3() -> bytes:
    if not BL.exists():
        pytest.skip("falta bootloader.bin (no versionado)")
    return BL.read_bytes()


def _at(d: bytes, addr: int, n: int) -> bytes:
    return d[addr - L3 + OFF3 : addr - L3 + OFF3 + n]


def test_solo_dos_ordenes_y_ninguna_escribe():
    d = _l3()
    # adr de c01f37d8/c01f37e8: únicas cadenas comparadas (5 B) por la consola
    assert _at(d, 0xC01F38D0, 6) == b"beast\0"
    assert _at(d, 0xC01F38D8, 6) == b"ldump\0"
    assert _at(d, 0xC01F393C, 13) == b"LD3:\nMEM_DUMP"
    # c01f3708 (volcado) solo lee: ldrb/ldrh/ldr [r4], ningún str
    body = _at(d, 0xC01F3708, 0xC01F376E - 0xC01F3708)
    assert body[0x3E:0x40] == bytes.fromhex("2278")  # c01f3746 ldrb r2,[r4]
    assert body[0x4C:0x4E] == bytes.fromhex("2288")  # c01f3754 ldrh r2,[r4]
    assert body[0x52:0x54] == bytes.fromhex("2268")  # c01f375a ldr r2,[r4]
    # Loader2 trae la misma consola (mismas cadenas, mismas dos órdenes)
    assert d.count(b"beast\0") == 2 and d.count(b"ldump\0") == 2


def test_bucle_de_led_inicializa_la_uart_y_sondea_la_consola():
    d = _l3()
    assert _at(d, 0xC01F3BB4, 8).hex() == "fff766fe01f026fa"  # bl c01f3884; bl c01f5008
    assert _at(d, 0xC01F3BC8, 4).hex() == "fff7e7fd"  # bl c01f379a (consola)
    # c01f5008: PL011 IBRD=0x1a, FBRD=3, LCRH=0x70, CR=0x701 (≈115 200 8N1 con 48 MHz)
    init = _at(d, 0xC01F503E, 0x1C)
    assert b"\x1a" in init[:4] and init[6:10].hex() == "4ff00302"


def test_salida_de_la_consola_apagada_con_backup_de_fabrica():
    from r14_backup import BK4  # type: ignore[import-not-found]

    d = _l3()
    # c01f376e (beast) sale si [0xc0060014]==0; c01f3636 pone +0x14 y +0 a 0 cuando 0x510015 != 1
    assert _at(d, 0xC01F3776, 4).hex() == "68690028"
    assert _at(d, 0xC01F3638, 6).hex() == "6c61ac612c60"
    dumps = sorted(ROOT.glob("analysis/camera-dumps/**/backup_flash.bin"))
    if not dumps:
        pytest.skip("sin volcados BK4")
    assert {BK4.load(p).read(0x510015) for p in dumps} == {b"\x00"}


def test_espera_de_ice_por_gpio_del_backup():
    from r14_backup import BK4  # type: ignore[import-not-found]

    d = _l3()
    assert _at(d, 0xC01F0CC2, 4).hex() == "03f003fe"  # bl c01f48cc, antes de c01f0cca
    lit = struct.pack("<I", 0xF90449)
    assert _at(d, 0xC01F4900, 4) == lit
    assert b"CFG:Wait ICE\n" in d
    dumps = sorted(ROOT.glob("analysis/camera-dumps/**/backup_flash.bin"))
    if not dumps:
        pytest.skip("sin volcados BK4")
    # banco 14, bit 17: c01f48b6 lee 0xf2910000 + (14 << 8) + 0x10
    assert {
        (BK4.load(p).read(0xF90449), BK4.load(p).read(0xF9044A)) for p in dumps
    } == {(bytes.fromhex("0e000000"), bytes.fromhex("11000000"))}
