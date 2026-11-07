"""E26-R75: verificación de R74 (av-cam.bin 3.21) y de la secuencia A/B de Darwin (darwin_core.bin 3.21)."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked"
AV = FW / "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
DZ = FW / "0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
pytestmark = pytest.mark.skipif(not (AV.is_file() and DZ.is_file()), reason="firmware original ausente")


def _dis(path: Path, base: int, a: int, n: int, mode: int) -> list[str]:
    md = capstone.Cs(capstone.CS_ARCH_ARM, mode)
    d = path.read_bytes()
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[a - base:a - base + 4 * n], a)][:n]


def _bionz(a: int, n: int) -> list[str]:
    return _dis(AV, 0x43541000, a, n, capstone.CS_MODE_THUMB)


def _darwin_bytes(a: int, n: int) -> bytes:
    return DZ.read_bytes()[a - 0x4200:a - 0x4200 + n]


def test_clase_solo_se_calcula_con_byte15_cero():
    # 0x438412be: r5 = [obj+0x15]; cbnz r5 -> salta 0x43842158 (el umbral 0x3012b)
    assert _bionz(0x438412BC, 4)[1:3] == ["ldrb r5, [r3, #0x15]", "cbnz r5, #0x438412e8"]
    assert _bionz(0x438412D0, 1) == ["bl #0x43842158"]


def test_umbral_solo_con_cap41c_1_y_byte2_cero():
    ins = _bionz(0x4384219E, 10)
    assert ins[:3] == ["ldr.w r1, [r7, #0x41c]", "cmp r1, #1", "bne #0x438421e2"]
    assert ins[3:5] == ["ldrb r2, [r3, #2]", "cbnz r2, #0x438421c4"]
    assert _bionz(0x438421E2, 4)[2:4] == ["movs r1, #3", "str r1, [r2, #0x60]"]  # resto: clase 3


def test_darwin_tipo_mecanismo_y_secuencia_b():
    # 0x20c74 -> 0x1b080(0): ([0x200002c0] != 0 ? [0x20000050] : 0) & 7
    assert struct.unpack_from("<II", DZ.read_bytes(), 0x1B0E0 - 0x4200) == (0x200002C0, 0x20000000)
    # B (0x2041e, arg 0) arranca la secuencia 02 04 06 10 11 en la máquina 0 (0x29d90 - 0x12 = 0x29d7e)
    assert _darwin_bytes(0x29D7E, 5) == bytes([2, 4, 6, 0x10, 0x11])
    # id 4 de la tabla 0x29e00 es 0x207e8 (P4E <- 0 vía 0x20cd4) y A/B retardados comparten la máquina 2 (0x29dc8)
    tab = struct.unpack_from("<8I", DZ.read_bytes(), 0x29E00 - 0x4200)
    assert (tab[6], tab[7]) == (4, 0x207E9)
