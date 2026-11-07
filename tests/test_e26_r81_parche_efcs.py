"""E26-R81: el hueco 0x13d5a del parche R76 pertenece a una funcion viva (0x13d58, llamada desde 0x1516c)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e26_r76"))
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
pytestmark = pytest.mark.skipif(not DARWIN.exists(), reason="falta darwin_core.bin")
BASE = 0x4200


def _bl_target(img: bytes, addr: int) -> int:
    """Destino de un BL Thumb-2 (T1) calculado a mano desde los dos halfwords."""
    h1, h2 = struct.unpack_from("<HH", img, addr - BASE)
    assert h1 >> 11 == 0b11110 and h2 >> 14 == 0b11 and h2 & 0x1000
    s = (h1 >> 10) & 1
    j1, j2 = (h2 >> 13) & 1, (h2 >> 11) & 1
    i1, i2 = 1 - (j1 ^ s), 1 - (j2 ^ s)
    off = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
    off -= (1 << 25) if s else 0
    return addr + 4 + off


def test_bl_1516c_llama_a_13d58():
    img = DARWIN.read_bytes()
    assert _bl_target(img, 0x1516C) == 0x13D58
    assert img[0x13D58 - BASE:0x13D5C - BASE] == bytes.fromhex("ff4910b5")   # ldr r1,[pc,#0x3fc]; push {r4,lr}


def test_parchear_rechaza_el_hueco_vivo():
    pytest.importorskip("capstone")
    import e26_r76_parche_darwin_tabla as P
    img = DARWIN.read_bytes()
    assert any(r[0] == 0x1516C for r in P.referencias_externas(img, P.FUNC_REAL, P.CAVE_END))
    with pytest.raises(RuntimeError, match="BLOQUEADO"):
        P.parchear_hueco_r76(img)
