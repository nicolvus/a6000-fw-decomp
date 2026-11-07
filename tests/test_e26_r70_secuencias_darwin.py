"""E26-R70: quién sube P4C, orden respecto a A, y qué toca la máquina de `ip` (darwin_core.bin 3.21)."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
capstone = pytest.importorskip("capstone")
BASE = 0x4200
pytestmark = pytest.mark.skipif(not DARWIN.is_file(), reason="darwin_core.bin original ausente")


def _d() -> bytes:
    return DARWIN.read_bytes()


def _w(a: int) -> int:
    return struct.unpack_from("<I", _d(), a - BASE)[0]


def _dis(addr: int, n: int) -> list[str]:
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    d = _d()
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(d[addr - BASE:addr - BASE + 4 * n], addr)][:n]


def _seq(a: int, n: int) -> list[int]:
    d, out = _d(), []
    while d[a - BASE] < n:
        out.append(d[a - BASE])
        a += 1
    return out


def test_p4c_sube_en_la_preparacion_antes_de_armar_a():
    assert _dis(0x1817C, 2) == ["bl #0x17cee", "bl #0x1961c"]          # P4C <- 1 y luego secuencia de captura
    assert _dis(0x17CEE, 2)[1] == "bl #0x16e7a"                         # 0x16e7a: P4C <- 1
    assert _w(0x28FDC) == 0x28FF8 and _w(0x28FF8 + 8 * 0x1F) == 0x1F and _w(0x28FFC + 8 * 0x1F) == 0x190FD
    for k in (0x54, 0x44, 0x34, 0x22, 0x12):                          # las cinco secuencias de 0x1961c
        assert 0x1F in _seq(0x28FDC - k, 0x31)


def test_paso_0x1f_arma_a_y_b_y_despues_la_secuencia_posterior():
    assert _dis(0x19128, 1) == ["bl #0x18d6e"]
    assert _dis(0x19132, 2) == ["bl #0x17064", "bl #0x1e6ba"]
    assert _dis(0x1E6CE, 2) == ["sub.w r1, r0, #0xa", "bl #0x1e150"]   # 0x296f0 − 0xa
    assert _seq(0x296E6, 0xF) == [0x0D, 0x05, 0x02, 0x03, 0x0A, 0x04, 0x06, 0x09]
    assert _w(0x2970C + 8 * 4) == 5 and _w(0x29710 + 8 * 4) == 0x1EA5D  # acción 5
    assert _dis(0x1EA60, 2) == ["movs r0, #1", "bl #0x16e92"]
    assert _dis(0x16E9A, 2) == ["sub.w r1, r0, #0xf", "bl #0x1e150"]   # 0x28dd4 − 0xf
    assert _seq(0x28DC5, 0x32) == [0x30, 0x0F, 0x10, 0x2F, 0x14, 0x15, 0x16, 0x17, 0x18, 0x2F, 0x19, 0x1A, 0x1B, 0x1C]
    assert _w(0x28ED0) == 0x14 and _w(0x28ED4) == 0x175EB              # acción 0x14 -> 0x175ea
    assert _dis(0x175EE, 1) == ["bl #0x16e7a"]                          # P4C <- 1 (rearme)


def test_maquina_de_ip_no_toca_lineas_de_cortina():
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB | capstone.CS_MODE_MCLASS)
    d, offs, prev = _d(), set(), None
    for i in md.disasm(d[0x23CF6 - BASE:0x24400 - BASE], 0x23CF6):
        if i.mnemonic in ("bl", "b.w") and i.op_str == "#0x51c0" and prev and prev.startswith("mov"):
            offs.add(int(prev.split("#")[1], 0))
        if i.mnemonic in ("mov.w", "movs", "mov") and i.op_str.startswith("r0, #"):
            prev = f"{i.mnemonic} {i.op_str}"
    assert offs >= {0x228, 0x14, 0x194, 0x298}
    assert not offs & {0x22C, 0x230, 0x234, 0x238}                     # P4B–P4E
