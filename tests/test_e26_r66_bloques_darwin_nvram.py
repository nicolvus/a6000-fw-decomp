"""E26-R66: los bloques B/G de Darwin son las propiedades NVRAM 0x1850001/0x1850000 (tabla BIONZ 0x43fe8c38), no BK4 0x30102."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
AV_BASE, TABLE = 0x43541000, 0x43FE8C38
# id de propiedad -> (bloque Darwin, tamaño, banderas)
EXPECTED = {
    0x1850001: (0x20280, 0x180, 0xF),       # B = 0x20000300
    0x1850000: (0x10100, 0x80, 0xF),        # G = 0x20000480
    0x1850004: (0x20000500, 0x100, 0x1F),   # lectura desde Darwin
    0x1850005: (0x30100, 0x100, 0x1F),      # lectura desde Darwin (0x20000600)
}


@pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin ausente")
def test_tabla_bionz_de_bloques_darwin():
    d = AVCAM.read_bytes()
    found = {}
    for k in range(4):
        tag, flags, pid, handler, _, addr, size = struct.unpack_from("<7I", d, TABLE - AV_BASE + 0x24 * k)
        assert tag == 0x185 and handler == 0x436BC515
        found[pid] = (addr, size, flags)
    assert found == EXPECTED
    assert struct.pack("<I", 0x30102) not in d[TABLE - AV_BASE:TABLE - AV_BASE + 0x90]
