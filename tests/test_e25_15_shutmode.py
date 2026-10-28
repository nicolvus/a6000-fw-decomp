"""E25-15 — bytes y emulación en los que se apoya
docs/capture/e25-15-shutmode0-temporizacion-nativa.md.

Se omite si el firmware no está disponible (no se versiona). No toca la cámara.
"""
from __future__ import annotations

import hashlib
import importlib.util
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW_A6000 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
FW_A7S = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
SHA_A6000 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
SHA_A7S = "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e"

pytestmark = pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")


def at(addr: int, n: int) -> bytes:
    with FW_A6000.open("rb") as f:
        f.seek(addr - BASE)
        return f.read(n)


def hx(addr: int, n: int) -> str:
    return at(addr, n).hex()


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bl_targets(data: bytes):
    """BL/BLX/B.W Thumb-2: devuelve (dirección, destino, tipo)."""
    base = BASE
    h = memoryview(data)[: len(data) - len(data) % 2].cast("H")
    for i in range(len(h) - 1):
        a, b = h[i], h[i + 1]
        if a & 0xF800 != 0xF000 or not (b & 0x8000):
            continue
        kind = "bl" if b & 0x5000 == 0x5000 else "blx" if b & 0x5000 == 0x4000 else "b" if b & 0x5000 == 0x1000 else None
        if kind is None:
            continue
        s = (a >> 10) & 1
        j1 = (b >> 13) & 1
        j2 = (b >> 11) & 1
        i1 = ~(j1 ^ s) & 1
        i2 = ~(j2 ^ s) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((a & 0x3FF) << 12) | ((b & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        pc = base + 2 * i + 4
        t = pc + imm
        if kind == "blx":
            t &= ~3
        yield base + 2 * i, t, kind


# --- identidad -----------------------------------------------------------------

def test_sha_a6000():
    assert sha(FW_A6000) == SHA_A6000


@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_sha_a7s():
    assert sha(FW_A7S) == SHA_A7S


# --- secuencia de captura 0x438c828c -------------------------------------------

def test_capture_builds_both_blocks_before_calls():
    data = FW_A6000.read_bytes()
    targets = {(a, t) for a, t, k in bl_targets(data) if k in ("bl", "blx")}
    # 0x438c829c -> 0x437f8a50 (constructor de cap+0x64c y cap+0x6bc)
    assert (0x438C829C, 0x437F8A50) in targets
    # 0x438c830c -> 0x436d6320 (wrapper SetExposure)
    assert (0x438C830C, 0x436D6320) in targets
    # 0x438c831e -> 0x436d6398 (wrapper +0x30)
    assert (0x438C831E, 0x436D6398) in targets
    assert [0x438C829C, 0x438C830C, 0x438C831E] == sorted([0x438C829C, 0x438C830C, 0x438C831E])
    # bloques pasados
    assert hx(0x438C8302, 8) == "04f5c8610c31b6f8"  # r1 = cap+0x64c
    assert hx(0x438C8314, 8) == "04f5d6610c31b6f8"  # r1 = cap+0x6bc


def test_capture_mode_2_3_forces_shutmode0_r5_2():
    # param+9=0, param+4=0, param+0=2, param+6=0, param+8=0
    assert hx(0x438C82B8, 24) == "0023022184f85536a4f85036c4f84c16a4f8523684f85436"


# --- constructores de los bloques ---------------------------------------------

def test_frame_record_copies_16b_to_cap_64c():
    # add r3,r0,#0x64 ; mov r5,r0 ; ldm r3,{r0-r3} ; stm lr,{r0-r3} ; add r3,r5,#0x74
    assert hx(0x4383FDAA, 8) == "00f1640305460fcb"
    assert hx(0x4383FDB0, 2) == "0fcb"        # ldm r3,{r0-r3}
    assert hx(0x4383FDB2, 4) == "8ee80f00"    # stm lr,{r0-r3}
    assert hx(0x4383FDB6, 4) == "05f17403"


def test_437f8a50_writes_cap_6bc_from_scratch():
    # ldrh [sp,#0xa] -> cap+0x6be ; ldrh [sp,#8] -> cap+0x6bc
    assert hx(0x437F8AB2, 20) == "bdf80a30bdf80820a4f8be36bdf81030a4f8bc26"


def test_record_r5_comes_from_record_0x1c():
    # str r0,[r5,#0x64] (r0 = record+0x1c) y str r2,[r5,#0x64] en la rama sin EFCS
    assert hx(0x43841710, 2) == "6866"
    assert hx(0x438417D0, 2) == "6a66"


# --- bloques de comandos --------------------------------------------------------

def test_setexposure_command_fields():
    # blk+0x50=r1, +0x52=r2, +0x54=r3, +0x57=byte, +0x56=byte
    assert hx(0x43AD9A4A, 20) == "a0f85010a0f85220a0f8543080f8575080f85640"


def test_setread_command_fields():
    # blk+0x66=r1, +0x68=r2, +0x6a=r3, +0x6c=r4
    assert hx(0x43AD9A66, 16) == "a0f86610a0f86820a0f86a30a0f86c40"


def test_setread_calls_conversion_and_block_filler():
    data = FW_A6000.read_bytes()
    targets = {(a, t) for a, t, k in bl_targets(data) if k in ("bl", "blx")}
    assert (0x436D7EAE, 0x436D8A90) in targets
    assert (0x436D7F56, 0x43AD9A60) in targets


def test_conversion_callers_are_the_two_read_methods():
    data = FW_A6000.read_bytes()
    callers = sorted({a for a, t, k in bl_targets(data) if k in ("bl", "blx") and t == 0x436D8A90})
    # 0x436d7546 = SetReadZ (+0x34); 0x436d7eae = SetRead (+0x30). SetExposure no la usa.
    assert callers == [0x436D7546, 0x436D7EAE]


@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_uses_0x60_for_setread():
    with FW_A7S.open("rb") as f:
        f.seek(0x43ADA068 - BASE)
        b = f.read(16)
    assert b.hex() == "a0f86010a0f86220a0f86430a0f86640"
    assert hx(0x43AD9A66, 2) == "a0f8"  # A6000: 0x66, no 0x60 (prefijo distinto)
    assert hx(0x43AD9A68, 2) == "6610"


def test_vtable_28_30_34_are_setexposure_setread_setreadz():

    vt = at(0x43FCC0B8, 12)  # +0x28, +0x2c, +0x30 (Thumb)
    vals = struct.unpack("<III", vt)
    assert vals[0] == 0x436D6F6D  # SetExposure
    assert vals[2] == 0x436D7E09  # SetRead (+0x30)
    assert struct.unpack("<I", at(0x43FCC0C4, 4))[0] == 0x436D74B9  # SetReadZ (+0x34)


@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_0x34_is_not_setreadz():

    with FW_A7S.open("rb") as f:
        f.seek(0x43FCE084 - BASE)
        assert struct.unpack("<I", f.read(4))[0] == 0x43AD9859  # A7S +0x34
        f.seek(0x43AD9858 - BASE)
        assert f.read(2).hex() == "0520"  # movs r0,#5 (no soportado)


# --- emulación ------------------------------------------------------------------

def _emu_module():
    pytest.importorskip("unicorn")
    pytest.importorskip("capstone")
    spec = importlib.util.spec_from_file_location("e25_15_emu", ROOT / "scripts/e25_15_emu.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_emulation_scenarios_differ_only_in_r5_and_shutmode():
    m = _emu_module()
    emu = m.Emu()
    for speed in ("1/8000", "1/4000", "1/1000", "1/250", "1/60"):
        us = m.tv_us(emu, m.SPEEDS[speed])
        r5c = m.r5_from_us(us)
        a = m.scenario(emu, 1, 3, m.SR_CODE)
        b = m.scenario(emu, 1, 0, m.SR_CODE)
        c = m.scenario(emu, max(0, r5c), 0, m.SR_CODE)

        assert a["setread"]["cmd"] == b["setread"]["cmd"] == c["setread"]["cmd"]
        assert a["setexposure"]["cmd"]["blk+0x52"] == 1
        assert b["setexposure"]["cmd"]["blk+0x52"] == 1
        assert c["setexposure"]["cmd"]["blk+0x52"] == max(0, r5c)
        assert a["setexposure"]["cmd"]["blk+0x57"] == 3
        assert b["setexposure"]["cmd"]["blk+0x57"] == 0
        assert c["setexposure"]["cmd"]["blk+0x57"] == 0
        # +0x30 no toca el bloque de SetExposure ni el contador
        for k in ("blk+0x50", "blk+0x52", "blk+0x54", "blk+0x56", "blk+0x57", "obj+0x3a0"):
            assert k not in a["setread"]["cmd"]
        # SetExposure no toca el bloque de +0x30
        for k in ("blk+0x66", "blk+0x68", "blk+0x6a", "blk+0x6c"):
            assert k not in a["setexposure"]["cmd"]


def test_emulation_conversion_is_position_not_integration():
    m = _emu_module()
    emu = m.Emu()
    vals = {code: m.conv(emu, code) for code in (0x0A00, 0x0B00, 0x0C00, 0x0D00, 0x0E00, 0x0F00, 0x0FE0, 0x0FF0, 0x0FFF)}
    assert vals[0x0A00] == 4031
    assert vals[0x0B00] == 3967
    assert vals[0x0F00] == 2047
    assert vals[0x0FFF] == 11
    assert all(0 <= v <= 4095 for v in vals.values())
    # monótona decreciente en el tramo útil
    seq = [vals[k] for k in (0x0B00, 0x0C00, 0x0D00, 0x0E00, 0x0F00, 0x0FE0, 0x0FF0, 0x0FFF)]
    assert seq == sorted(seq, reverse=True)


# --- aritmética de 1/8000 -------------------------------------------------------

def test_precision_1_8000():
    lines = 125 / 15.2
    assert 8.22 < lines < 8.23
    assert abs(8 * 15.2 - 121.6) < 1e-9
    assert abs(9 * 15.2 - 136.8) < 1e-9
    assert abs((121.6 - 125) / 125 * 100 + 2.72) < 0.05
    assert abs((136.8 - 125) / 125 * 100 - 9.44) < 0.05
    assert round(4219 - lines) == 4211
