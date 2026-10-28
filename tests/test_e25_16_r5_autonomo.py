"""E25-16 — verificación de la cadena Tv → tiempo → líneas → r5 y del diseño
autónomo descrito en docs/capture/e25-16-r5-autonomo-fotografia.md.

Se omite si el firmware no está disponible (no se versiona). No toca la cámara.
"""
from __future__ import annotations

import hashlib
import importlib.util
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

# direcciones clave (fw 3.21)
TV_US = 0x4382FAC8          # Tv -> µs
TV_Q8 = 0x4382FA94          # Tv -> 1/256 µs (con clamp 0xC00)
UIDIV = 0x4355FAF0          # __aeabi_uidiv (truncante)
VTS = 0x4385DE94            # longitud de cuadro
TV_TO_R5 = 0x4383FA40       # Tv -> líneas -> r5 (ruta de foto, nativa)
BUILDER = 0x437B43B4        # constructor del registro de foto
EFCS_BUILDER = 0x43841070   # variante EFCS
CAPTURE = 0x438C828C        # secuencia de captura
SETEXPOSURE = 0x436D6F6C
SETREAD = 0x436D7E08

LINE_US = 15.2
LINE_Q8 = round(LINE_US * 256)      # 3891
VTS_MEASURED = 4219

pytestmark = pytest.mark.skipif(not FW.exists(), reason="firmware A6000 no versionado")


def at(addr: int, n: int) -> bytes:
    with FW.open("rb") as f:
        f.seek(addr - BASE)
        return f.read(n)


def hx(addr: int, n: int) -> str:
    return at(addr, n).hex()


def w16(addr: int) -> int:
    return struct.unpack("<H", at(addr, 2))[0]


def w32(addr: int) -> int:
    return struct.unpack("<I", at(addr, 4))[0]


def sha() -> str:
    h = hashlib.sha256()
    with FW.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bl_targets(data: bytes):
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


# --- 1. identidad del binario ---------------------------------------------------

def test_sha_firmware():
    assert sha() == SHA


# --- 2. origen del Tv: settings+0x162 -> record+0xf6 ----------------------------

def test_tv_copied_to_record_f6_before_conversion():
    """0x437b465e..0x437b4674: [settings+0x160]→+0xfa, [settings+0x162]→+0xf6 (Tv),
    [settings+0x15e]→+0xf8."""
    assert hx(0x437B4662, 4) == "bbf86221"   # ldrh.w r2,[fp,#0x162]  (Tv)
    assert hx(0x437B4666, 4) == "bbf85e31"   # ldrh.w r3,[fp,#0x15e]
    assert hx(0x437B466A, 4) == "a5f8fa10"   # strh.w r1,[r5,#0xfa]
    assert hx(0x437B4670, 4) == "a5f8f620"   # strh.w r2,[r5,#0xf6]  (Tv)
    assert hx(0x437B4674, 4) == "a5f8f830"   # strh.w r3,[r5,#0xf8]


def test_gate_and_native_conversion_in_normal_builder():
    """0x437b46c6 (gate cap+0x11b0) y 0x437b46d0 (llamada a 0x4383fa40)."""
    assert hx(0x437B46C6, 4) == "9af81830"   # ldrb.w r3,[sl,#0x18]
    assert hx(0x437B46CC, 2) == "3946"       # mov r1,r7
    assert hx(0x437B46CE, 2) == "2846"       # mov r0,r5
    assert hx(0x437B46D0, 4) == "8bf0b6f9"   # bl 0x4383fa40


def test_native_conversion_writes_r5_and_shutmde0():
    """0x4383fa40 escribe +0x64 (r5), +0x6c y +0x6d (=0) y +0xf0 (líneas)."""
    assert hx(0x4383FACC, 4) == "c4f864a0"   # str.w sl,[r4,#0x64]
    assert hx(0x4383FAD0, 4) == "84f86c30"   # strb.w r3,[r4,#0x6c]
    assert hx(0x4383FAD4, 4) == "84f86d30"   # strb.w r3,[r4,#0x6d]  -> ShutMode 0
    assert hx(0x4383FAD8, 4) == "c4f8f090"   # str.w sb,[r4,#0xf0]


def test_native_conversion_uses_uidiv_and_0xc54_threshold():
    assert hx(0x4383FA5C, 4) == "20f548f8"   # bl 0x4355faf0
    assert hx(0x4383FA68, 4) == "40f65443"   # movw r3,#0xc54
    assert hx(0x4383FA7A, 4) == "f0f725f8"   # bl 0x4382fac8
    assert hx(0x4383FA82, 4) == "f0f707f8"   # bl 0x4382fa94
    assert w32(0x4383FAFC) == 0x00825700     # constante de longitud de cuadro


def test_tv_settings_writer_in_capture_path():
    """0x437b4340 escribe [ajustes+0x162] desde una tabla si el modo es 9."""
    assert hx(0x437B4344, 4) == "d1f89432"   # ldr.w r3,[r1,#0x294]
    assert hx(0x437B43A2, 4) == "a4f86231"   # strh.w r3,[r4,#0x162]
    callers = {a for a, t, k in bl_targets(FW.read_bytes()) if t == 0x437B4340}
    # llamadas desde 0x437b45b8 (constructor normal) y 0x438412aa (EFCS)
    assert callers == {0x437B45B8, 0x438412AA}


# --- 3. conversión Tv -> tiempo -------------------------------------------------

@pytest.fixture(scope="module")
def emu():
    spec = importlib.util.spec_from_file_location(
        "e2516_emu", ROOT / "scripts/e25_16/emular_r5.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name,tv,us", [
    ("1/8000", 0x1CF7, 125),
    ("1/4000", 0x1BF7, 250),
    ("1/2000", 0x1AF7, 500),
    ("1/1000", 0x19F7, 1000),
    ("1/500", 0x18F7, 2001),
    ("1/250", 0x17F7, 4002),
    ("1/125", 0x16F7, 8005),
    ("1/60", 0x15E8, 16674),
])
def test_tv_a_microsegundos(emu, name, tv, us):
    h = emu.Harness()
    assert h.tv_us(tv) == us


def test_tv_q8_con_clamp(emu):
    h = emu.Harness()
    assert h.call(TV_Q8, 0x1000, 0) == 256_000_000     # 1 s exacto
    assert h.call(TV_Q8, 0x0C00, 0) == 0xFFFFFFFF      # clamp (>=16 s no representable)
    # 1/4000 = 250,164 µs: Q8 = 64042; la variante entera 0x4382fac8 trunca a 250
    assert h.call(TV_Q8, 0x1BF7, 0) == 64042
    assert h.tv_us(0x1BF7) == 250


# --- 4. longitud de cuadro nativa ----------------------------------------------

def test_vts_nativo_y_multiplicador(emu):
    h = emu.Harness()
    assert h.vts(600, 1, 0) == 4266
    assert h.vts(600, 2, 0) == 8532
    assert h.vts(0, 1, 0) == 1
    assert h.vts(3891, 1, 0) == 657


def test_vts_nativo_no_es_el_limite_efectivo(emu):
    """4266 (firmware) ≠ 4219 (punto de envolvente medido en T046)."""
    h = emu.Harness()
    vts = h.vts(600, 1, 0)
    assert vts == 4266
    assert vts - VTS_MEASURED == 47
    # con VTS nativo, 1/8000 y 1/4000 quedan por encima de 4219 -> envolvente
    for tv in (0x1CF7, 0x1BF7):
        lines = h.uidiv(h.tv_us(tv) * 256, LINE_Q8)
        assert vts - lines > VTS_MEASURED


# --- 5. cálculo de r5 y comparación con T047 ------------------------------------

@pytest.mark.parametrize("name,tv,r5_t047", [
    ("1/4000", 0x1BF7, 4203),
    ("1/1000", 0x19F7, 4153),
    ("1/250", 0x17F7, 3956),
    ("1/60", 0x15E8, 3122),
])
def test_r5_reproduce_t047(emu, name, tv, r5_t047):
    """La función nativa 0x4383fa40, ejecutada con VTS=4219, da el r5 medido."""
    h = emu.Harness()
    r5 = h.native_r5(tv)
    assert abs(r5 - r5_t047) <= 1, (name, r5, r5_t047)


def test_funcion_nativa_satura_en_cero(emu):
    """Para T > un cuadro, 0x4383fa40 escribe r5=0 (no negativo): negro, no exposición."""
    h = emu.Harness()
    for tv in (0x13E8, 0x1300, 0x1000, 0x0B18):   # 1/15, 1/8, 1 s, 30 s
        assert h.native_r5(tv) == 0


def test_limite_de_un_cuadro(emu):
    h = emu.Harness()
    us = h.tv_us(0x13E8)                     # 1/15
    lines = h.uidiv(us * 256, LINE_Q8)
    assert lines > VTS_MEASURED - 1          # no representable
    assert VTS_MEASURED - lines < 1


def test_no_se_acepta_r5_negativo(emu):
    h = emu.Harness()
    for tv in (0x13E8, 0x1300, 0x1000, 0x0B18):   # 1/15, 1/8, 1 s, 30 s
        lines = h.uidiv(h.tv_us(tv) * 256, LINE_Q8)
        r5 = VTS_MEASURED - lines
        assert r5 < 0, "el diseño debe rechazar estas velocidades, no escribirlas"


# --- 6. entrega a SetExposure ---------------------------------------------------

def test_setexposure_recibe_r5_y_shutmode0(emu):
    h = emu.Harness()
    cmd = h.setexposure(3956, 0)
    assert cmd.get("blk+0x52") == 3956
    assert cmd.get("blk+0x57") == 0


def test_secuencia_de_captura_ordena_constructor_y_setexposure():
    """El punto de intervención C3 está entre 0x437f8a50 y 0x436d6320."""
    assert hx(0x438C829C, 4) == "30f7d8fb"   # bl 0x437f8a50
    assert hx(0x438C8302, 4) == "04f5c861"   # add r1,cap,#0x64c
    assert hx(0x438C830C, 4) == "0ef608f8"   # bl 0x436d6320 (SetExposure)
    assert hx(0x438C8314, 4) == "04f5d661"   # add r1,cap,#0x6bc
    assert hx(0x438C831E, 4) == "0ef63bf8"   # bl 0x436d6398 (SetRead)


def test_ruta_de_parametros_no_se_reescribe_tras_el_constructor():
    """El bloque cap+0x64c sólo lo escribe 0x437f8a50 -> inyección posterior válida."""
    data = FW.read_bytes()
    calls = [a for a, t, k in bl_targets(data) if t == 0x437F8A50]
    assert calls == [0x438C829C]


def test_ambos_constructores_llaman_al_conversor_nativo():
    """0x4383fa40 lo usan el constructor normal y el de EFCS: no es código muerto."""
    data = FW.read_bytes()
    callers = {a for a, t, k in bl_targets(data) if t == 0x4383FA40}
    assert callers == {0x437B46D0, 0x438417C0}


def test_cap_1198_no_es_bloque_de_datos():
    """cap+0x1198 es el primer argumento de 0x4383fd6c, no un bloque de Tv.

    0x4383fd6c obtiene el registro global con 0x4383fb6c y copia *record+0x64*;
    no lee +0x162 desde cap+0x1198.
    """
    assert hx(0x437F8A8E, 4) == "04f58c55"   # add.w r5,r4,#0x1180
    assert hx(0x437F8A92, 4) == "05f11805"   # add.w r5,r5,#0x18  -> cap+0x1198
    assert hx(0x437F8AA4, 4) == "47f062f9"   # bl 0x4383fd6c (r0=cap+0x1198)
    assert hx(0x4383FDA0, 4) == "fff7e4fe"   # bl 0x4383fb6c (registro global)
    assert hx(0x4383FDAA, 4) == "00f16403"   # add.w r3,r0,#0x64
    assert hx(0x4383FDB0, 2) == "0fcb"       # ldm r3,{r0,r1,r2,r3}
