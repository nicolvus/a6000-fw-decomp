"""E25-14 — bytes de av-cam.bin (A7S 3.20 / A6000 3.21) en los que se apoya el informe
docs/capture/e25-14-imx235-imx210-exposicion-electronica.md.
Se omite si el firmware no está disponible (no se versiona)."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW_A7S = ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
FW_A6000 = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000

SHA_A7S = "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e"
SHA_A6000 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"


def at(fw: Path, addr: int, n: int) -> bytes:
    with fw.open("rb") as f:
        f.seek(addr - BASE)
        return f.read(n)


def hx(fw: Path, addr: int, n: int) -> str:
    return at(fw, addr, n).hex()


# --- identidad de los binarios -------------------------------------------------

@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_sha256_a7s():
    import hashlib

    h = hashlib.sha256()
    with FW_A7S.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    assert h.hexdigest() == SHA_A7S


@pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")
def test_sha256_a6000():
    import hashlib

    h = hashlib.sha256()
    with FW_A6000.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    assert h.hexdigest() == SHA_A6000


# --- SetExposure: contrato y despacho -----------------------------------------

@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_setexposure_contract():
    # push.w {r0-r10,lr}; mov r4,r0; ldr r3,[r0,#0x1ac]; mov r10,r1
    assert hx(FW_A7S, 0x436F4168, 12) == "2de9ff470446d0f8ac318a46"
    # ldrb.w r6,[r10,#9]  -> ShutMode = param+9
    assert hx(FW_A7S, 0x436F4198, 4) == "9af80960"
    # cmp r6,#4; bhi; tbb
    assert hx(FW_A7S, 0x436F423E, 8) == "042e5cd8dfe806f0"


@pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")
def test_a6000_setexposure_contract():
    # ldr.w r3,[r0,#0x170]; push.w {r4-r11,lr}; cmp r3,#0x11
    assert hx(FW_A6000, 0x436D6F6C, 12) == "d0f870312de9f04f112bdff8"
    # ldrb.w r9,[r1,#9]
    assert hx(FW_A6000, 0x436D6FB6, 4) == "91f80990"
    # cmp r9,#4; bhi.w
    assert hx(FW_A6000, 0x436D70BE, 8) == "b9f1040f00f2e480"


# --- bits de configuración de ShutMode 0 --------------------------------------

@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_shutmode0_bits():
    # bfc b2; bfc b6; luego bfc b4; cfg2 |= 8
    assert hx(FW_A7S, 0x436F424C, 18) == "19796ff38201197119796ff386113ae01979"
    assert hx(FW_A7S, 0x436F42D2, 10) == "197119796ff304111971"


@pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")
def test_a6000_shutmode0_bits():
    # bfc b2; bfc b7; bfc b4; orr b6
    assert hx(FW_A6000, 0x436D70D0, 18) == "9a786ff382029a709a786ff3c7126de09a78"
    assert hx(FW_A6000, 0x436D71BC, 18) == "9a709a786ff304129a709a7842f040029a70"


# --- método de velocidad +0x30 y rama 0x1000 ---------------------------------

@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_vtable_and_speed_method():
    # vtable 0x43fce050: +0x28 = SetExposure, +0x30 = método de velocidad (Thumb)
    assert hx(FW_A7S, 0x43FCE078, 8) == "69416f435598ad43"
    assert hx(FW_A7S, 0x43FCE080, 8) == "954a6f435998ad43"
    # el método guarda el tercer argumento (armado) en [sp,#0x30]
    assert hx(FW_A7S, 0x436F4AA8, 4) == "0c931129"
    # cmp r8,#0x1000; add r8,#0x1000; flag +0x3d7
    assert hx(FW_A7S, 0x436F4B0C, 24) == "bdf83880b8f5805f17d908f58053012104f59e7084f8d713"


@pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")
def test_a6000_vtable_and_speed_method():
    assert hx(FW_A6000, 0x43FCC0B8, 8) == "6d6f6d43e5676d43"
    assert hx(FW_A6000, 0x43FCC0C0, 8) == "097e6d43b9746d43"
    # prólogo: no guarda r3 (no hay `str r3,[sp,...]`); fija obj+0x3a3=1
    assert hx(FW_A6000, 0x436D7E08, 8) == "2de9f0478846d0f8"
    assert hx(FW_A6000, 0x436D7E1C, 8) == "7d4484f8a37312d1"
    # cmp r3,#0x1000; addhi r3,#0x1000; rsbhi r6,r6,r3
    assert hx(FW_A6000, 0x436D7E9A, 16) == "b3f5805f83bf03f58053c6eb0306adf8"


# --- armado de exposición larga: A7S sí, A6000 no en el método ----------------

@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_long_exposure_arm_state():
    # 0x436f43c0: lee obj+0x3dc, si 1 -> estado 2 y 0x43b73044(0xe)
    assert hx(FW_A7S, 0x436F43C0, 8) == "d0f8dc3310b50446"
    assert hx(FW_A7S, 0x436F43F0, 8) == "d0f8dc3310b50446"
    assert b"\x0e\x20" in at(FW_A7S, 0x436F43DC, 8)  # movs r0,#0xe


@pytest.mark.skipif(not FW_A7S.exists(), reason="firmware A7S no versionado")
def test_a7s_capture_passes_arm_flag():
    # captura normal: movs r3,#0 antes del wrapper +0x30 (0x436f2988)
    assert hx(FW_A7S, 0x438B77B4, 12) == "04f5d661b5f8b02000233bf6"
    # ruta que arma: add.w r1,r4,#0x6b0; movs r2,#0; movs r3,#1; bl 0x436f2988
    assert hx(FW_A7S, 0x438B6EFA, 10) == "04f5d661002201233bf6"


@pytest.mark.skipif(not FW_A6000.exists(), reason="firmware A6000 no versionado")
def test_a6000_still_capture_calls_speed_method():
    # add.w r1,r4,#0x6b0; adds r1,#0xc; ldrh r2,[r6,#0x9c]; bl 0x436d6398
    assert hx(FW_A6000, 0x438C8314, 14) == "04f5d6610c31b6f89c200ef63bf8"


# --- tablas de tiempos por modo: 30 filas idénticas ---------------------------

@pytest.mark.skipif(not (FW_A7S.exists() and FW_A6000.exists()), reason="firmware no versionado")
def test_mode_timing_table_first_30_rows_equal():
    a = at(FW_A7S, 0x43BD8154, 30 * 12)
    b = at(FW_A6000, 0x43BDBF2E, 30 * 12)
    assert a == b
    # primera fila documentada
    assert a[:12].hex() == "cb38a4397e3a583b333c0e3d"


# --- aritmética de la ley medida (T046/T047) ---------------------------------

def test_ley_r5_t047():
    """E = (4219 - r5) * 15.2 us; valores de T047."""
    for r5, obj_ms in ((4203, 0.25), (4153, 1.00), (3956, 4.00), (3122, 16.7)):
        got_ms = (4219 - r5) * 15.2 / 1000.0
        assert abs(got_ms - obj_ms) / obj_ms < 0.06
