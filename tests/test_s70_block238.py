"""S70: +0x238/+0x280 del bloque 0x43edf684 solo se escriben (handlers por comando)."""
import struct
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parents[1] / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
pytestmark = pytest.mark.skipif(not BIN.is_file(), reason="falta av-cam.bin")


def word(addr: int) -> int:
    return struct.unpack_from("<I", BIN.read_bytes(), addr - BASE)[0]


def test_tabla_comandos_40e3_a_handler_238():
    assert word(0x43FFFC60) == 0x40E3
    assert word(0x43FFFC64) == 0x438032D5


def test_handlers_escriben_238_y_280():
    d = BIN.read_bytes()
    assert d[0x438032DC - BASE : 0x438032E0 - BASE] == bytes.fromhex("c3f83822")  # str.w r2,[r3,#0x238]
    assert d[0x43802614 - BASE : 0x43802618 - BASE] == bytes.fromhex("c3f88022")  # str.w r2,[r3,#0x280]


def test_accesor_puro_del_bloque():
    d = BIN.read_bytes()
    assert d[0x43804DEC - BASE : 0x43804DEE - BASE] == bytes.fromhex("7047")  # bx lr


def test_darwin_sin_literal_del_byte_de_tipo():
    f = BIN.parents[3] / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
    if not f.is_file():
        pytest.skip("falta darwin_core.bin")
    d = f.read_bytes()
    pool = {struct.unpack_from("<I", d, o)[0] for o in range(0, len(d) - 3, 4)}
    assert not any(0x20000050 <= v <= 0x20000058 for v in pool)
    assert struct.unpack_from("<2I", d, 0) == (0x20002A00, 0x45C9)
