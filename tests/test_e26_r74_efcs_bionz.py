"""E26-R74: en el EFCS oficial el BIONZ fija la línea de reinicio sin depender de T (av-cam.bin 3.21)."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AV = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
capstone = pytest.importorskip("capstone")
BASE = 0x43541000
pytestmark = pytest.mark.skipif(not AV.is_file(), reason="av-cam.bin original ausente")


def _w(a: int) -> int:
    return struct.unpack_from("<I", AV.read_bytes(), a - BASE)[0]


def _dis(a: int, n: int) -> list[str]:
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    d = AV.read_bytes()
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[a - BASE:a - BASE + 4 * n], a)][:n]


def test_sl_fijo_si_0x30097_byte15_no_es_1():
    # 0x438417b6: [0x30097+0x15]==1 -> 0x4383fa40 (sl depende de T); si no, record+0x64 = record+0x1c
    assert _dis(0x438417B6, 3) == ["ldrb r2, [r0, #0x15]", "cmp r2, #1", "bne #0x438417c6"]
    assert _dis(0x438417C6, 4)[0] == "ldrh r2, [r5, #0x1c]"
    assert _dis(0x438417C6, 4)[3] == "str r2, [r5, #0x64]"


def test_tablas_bk4_por_indice():
    ptr, ids = 0x43FF3200, 0x43FF2FAC
    assert {_w(ptr + 4 * k): _w(ids + 4 * k) for k in (36, 39, 40, 43)} == {
        0x43F6B7DE: 0x30087, 0x43F72B62: 0x30097, 0x43F76342: 0x30100, 0x43F73042: 0x3012B}
    got = 0x4401EEE4
    assert _w(got + _w(0x438418D8)) == 0x43F72B62   # pcVar22 del planificador EFCS = BK4 0x30097
    assert _w(got + _w(0x43842350)) == 0x43F73042   # umbral de clase de 0x43842158 = BK4 0x3012b
