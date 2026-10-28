"""T052-B0 — VTS, predicado de cuadro extra y viabilidad de C3-B.

Cubre, sin tocar la cámara:
  * la cadena `record+0x20 ← cap+0x5e0 ← descriptor+6` y el descriptor de modo;
  * el predicado `0x43a12ca8` y su bloque de NVRAM (0x100 B, +0x10 = 0);
  * la independencia de `record+0xf0` (líneas) respecto de VTS/predicado;
  * C3-A (r5 nativo directo) inválido con cuadro extra y C3-B (4219 − líneas);
  * el recolector `scripts/t052_b0_readonly.py` y su modo offline.

Las pruebas que necesitan el volcado de RAM o los backups NVRAM se omiten si
no están; una omisión no cuenta como verificación.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
DUMP = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
NVRAM = ROOT / "analysis/camera-dumps/20261020-first/backup_mem.bin"
SAMPLE = ROOT / "analysis/t052-b0/offline-sample.json"
BASE = 0x43541000
SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
RAM_OFF = 0x40000000
GOT = 0x4401EEE4
RECORD_A = 0x43EA5B4C
RECORD_B = 0x43EEE770
SETTINGS = 0x43F79F94
IMAGER = 0x43EA976C
GATE_B = 0x43F6E5C2
PREDICATE = 0x43DEB360
DESCRIPTOR = 0x43EA13DC
CTX = 0x43EAADD8
PRED_GOT = GOT + 0x64E8
NVRAM_OFF = 0x74218
NVRAM_BLOCK_SHA = "2a42df46c7f38bf4ac39e9de4df5e7af5686a27dfd272dba9e79866de57ae370"

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


def dump_u32(virt: int) -> int:
    with DUMP.open("rb") as f:
        f.seek(virt + RAM_OFF - 0x80000000)
        return struct.unpack("<I", f.read(4))[0]


def dump_bytes(virt: int, n: int) -> bytes:
    with DUMP.open("rb") as f:
        f.seek(virt + RAM_OFF - 0x80000000)
        return f.read(n)


# --- 1. identidad y cadena VTS -------------------------------------------------

def test_sha_firmware():
    assert sha() == SHA


def test_got_slots_apuntan_a_los_objetos():
    assert w32(GOT + 0x3764) == RECORD_A
    assert w32(GOT + 0x6F18) == RECORD_B
    assert w32(GOT + 0x1904) == SETTINGS
    assert w32(GOT + 0x2CC4) == IMAGER
    assert w32(GOT + 0x5F74) == GATE_B
    assert w32(PRED_GOT) == PREDICATE


def test_descriptor_a_cap_5e0_y_record_20():
    # cap+0x5e0 <- [descriptor+6]; record+0x20 <- cap+0x5e0
    assert hx(0x43846D9C, 2) == "ea6b"       # ldr r2,[r5,#0x3c]
    assert hx(0x43846E08, 2) == "db88"       # ldrh r3,[r3,#6]
    assert hx(0x43846E12, 4) == "a4f8e035"   # strh.w r3,[r4,#0x5e0]
    # el productor lee record+0x20, no una constante
    assert hx(0x4383FA66, 2) == "268c"       # ldrh r6,[r4,#0x20]
    assert hx(0x4383FA46, 2) == "c768"       # ldr r7,[r0,#0xc]


def test_descriptor_es_objeto_de_modo_en_dram():
    # La cadena de constructores ya está verificada por bytes; el ctx se
    # identificó por emulación (0x437b4eb4 -> 0x437b4df0 -> 0x437b5b14).
    assert hx(0x43844E80, 4) == "2de9f04f"   # push.w {r4-r11,lr}
    assert hx(0x437B5BA4, 4) == "8ff06cf9"   # bl 0x43844e80
    assert hx(0x437B4ED2, 4) == "fff78dff"   # bl 0x437b4df0
    assert hx(0x437B4E10, 4) == "00f080fe"   # bl 0x437b5b14


@pytest.mark.skipif(not DUMP.exists(), reason="volcado de RAM no disponible")
def test_descriptor_de_reposo_tiene_vts_cero():
    assert dump_u32(CTX + 0x3C) == DESCRIPTOR
    assert struct.unpack("<H", dump_bytes(DESCRIPTOR + 6, 2))[0] == 0
    assert struct.unpack("<H", dump_bytes(RECORD_A + 0x20, 2))[0] == 0


# --- 2. predicado y NVRAM ------------------------------------------------------

def test_predicado_lee_byte_y_devuelve_uno_para_0_o_1():
    assert hx(0x43A12CA8, 2) == "054b"
    assert hx(0x43A12CAA, 2) == "064a"
    assert hx(0x43A12CB0, 2) == "187c"       # ldrb r0,[r3,#0x10]
    assert hx(0x43A12CB2, 4) == "a0f10101"   # sub.w r1,r0,#1
    assert hx(0x43A12CB6, 2) == "4842"       # rsbs r0,r1,#0
    assert hx(0x43A12CB8, 4) == "40eb0100"   # adc.w r0,r0,r1


def test_predicado_es_selector_de_modo_de_captura():
    # Tres llamadores: productor, flags de captura y selector de tabla.
    assert hx(0x4383FA9A, 4) == "d3f105f9"   # bl 0x43a12ca8
    assert hx(0x438C7416, 4) == "4bf147fc"   # bl 0x43a12ca8
    assert hx(0x43A1415A, 4) == "fef7a5fd"   # bl 0x43a12ca8


@pytest.mark.skipif(not NVRAM.exists(), reason="backup NVRAM no disponible")
def test_bloque_predicado_es_copia_de_nvram_y_byte_10_cero():
    data = NVRAM.read_bytes()
    assert data[NVRAM_OFF:NVRAM_OFF + 7].hex() == "ffffff01020202"
    block = data[NVRAM_OFF:NVRAM_OFF + 0x100]
    assert block[0x10] == 0
    assert hashlib.sha256(block).hexdigest() == NVRAM_BLOCK_SHA


@pytest.mark.skipif(not (DUMP.exists() and NVRAM.exists()), reason="volcado/NVRAM no disponibles")
def test_bloque_ram_igual_a_nvram():
    ram = dump_bytes(PREDICATE, 0x100)
    nv = NVRAM.read_bytes()[NVRAM_OFF:NVRAM_OFF + 0x100]
    assert ram == nv
    assert ram[0x10] == 0
    assert hashlib.sha256(ram).hexdigest() == NVRAM_BLOCK_SHA
    assert dump_u32(PRED_GOT) == PREDICATE


# --- 3. contador de cuadros ----------------------------------------------------

def test_contador_68_se_copia_a_param_4_y_no_hay_acumulador():
    # 0x4383fd6c copia 16 B de record+0x64 a cap+0x64c; +0x68 -> param+4.
    assert hx(0x4383FDAA, 4) == "00f16403"   # add.w r3,r0,#0x64
    assert hx(0x4383FDB0, 4) == "0fcb8ee8"   # ldm.w r3,{r0,r1,r2,r3}
    assert hx(0x4383FDB2, 4) == "8ee80f00"   # stm.w lr,{r0,r1,r2,r3}
    # SetExposure lee param+0 (r5) y param+4 (ventana); no acumula cuadros.
    assert hx(0x436D6FAE, 2) == "0d88"       # ldrh r5,[r1]
    assert hx(0x436D6FAA, 2) == "8e88"       # ldrh r6,[r1,#4]
    assert hx(0x436D6FB6, 4) == "91f80990"   # ShutMode


# --- 4. emulación C3-A / C3-B --------------------------------------------------

def _load_emulator():
    spec = importlib.util.spec_from_file_location("t052b0_emu", ROOT / "scripts/t052_b0_emulate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_lineas_no_dependen_de_vts_ni_predicado():
    mod = _load_emulator()
    for tv in (0x1BF7, 0x17F7, 0x15E8):
        vals = {mod.run_case(tv, vts, extra)["lineas"] for vts in (4219, 4266, 1000) for extra in (0, 1)}
        assert len(vals) == 1


def test_c3a_con_cuadro_extra_es_invalido():
    mod = _load_emulator()
    for tv in (0x1BF7, 0x17F7, 0x15E8):
        case = mod.run_case(tv, 4219, 1)
        assert case["r5_nativo"] > 4219
        assert case["r5_nativo_valido"] == 0


def test_c3b_reproduce_t047():
    mod = _load_emulator()
    expected = {0x1BF7: 4203, 0x17F7: 3956, 0x15E8: 3122}
    for tv, want in expected.items():
        case = mod.run_case(tv, 4219, 1)  # incluso con cuadro extra activo
        assert case["lineas"] > 0
        assert case["r5_c3b"] == want
        assert case["r5_c3b_valido"] == 1


def test_c3b_no_necesita_vts_del_descriptor():
    mod = _load_emulator()
    for vts in (4219, 4266, 1000):
        assert mod.run_case(0x17F7, vts, 0)["r5_c3b"] == 3956


# --- 5. recolector -------------------------------------------------------------

def test_recolector_no_escribe_en_memoria_ni_usa_temporales_de_camara():
    src = (ROOT / "scripts/t052_b0_readonly.py").read_text()
    assert "nunca `of=/dev/mem`" in src
    assert src.count("of=/dev/mem") == 1  # solo la advertencia del docstring
    assert "os.system" not in src
    assert "subprocess" not in src
    assert "tee " not in src
    # El único acceso a /dev/mem es `dd if=`.
    assert src.count("/dev/mem") >= 1
    assert "dd if=/dev/mem" in src
    # T026: bs=1 con skip > 2^31 falla en la cámara; el lector usa bs=2.
    assert "bs=2" in src
    assert "dd if=/dev/mem bs=1" not in src


def test_modo_offline_produce_json_marcado_y_c3b():
    out = ROOT / "analysis/t052-b0" / "_test_offline.json"
    try:
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts/t052_b0_readonly.py"),
             "--offline", str(SAMPLE), "--label", "offline-1_250", "--out", str(out)],
            check=False, capture_output=True, text=True, cwd=ROOT,
        )
        assert r.returncode == 0, r.stderr
        d = json.loads(out.read_text())
        assert d["mode"] == "offline-sample"
        assert d["valid_as_physical_reading"] is False
        assert d["offline_notice"].startswith("DATOS DE EJEMPLO")
        assert d["derived"][-1]["c3b_r5_desde_lineas"] == 3956
        assert d["derived"][-1]["predicado_extra_frame"] == 1
    finally:
        out.unlink(missing_ok=True)


def test_modo_fisico_exige_confirmacion():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts/t052_b0_readonly.py"), "--label", "x"],
        check=False, capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 2
    assert "--confirm-readonly" in r.stderr


def test_muestra_offline_esta_marcada():
    d = json.loads(SAMPLE.read_text())
    assert d["source"] == "offline-sample"
    assert d["not_physical"] is True
    assert "predicate" in d["regions"]
    assert d["regions"]["predicate"][0x20:0x22] == "00"  # byte +0x10 = 0


# --- 6. evidencia ---------------------------------------------------------------

def test_evidencia_vts_y_predicado():
    v = json.loads((ROOT / "analysis/t052-b0/vts.json").read_text())
    assert v["chain"]["record_0x20"]["bytes_ok"] is True
    assert v["chain"]["descriptor"]["ctx_0x3c"] == "0x43ea13dc"
    assert "NO determinado" in v["static_conclusion"]
    r = json.loads((ROOT / "analysis/t052-b0/rea-xrefs.json").read_text())
    assert r["queries"]["xrefs_0x43deb360"] == ["0x43fea1f8"]
    assert r["queries"]["xrefs_0x43844e80"] == ["0x437b5ba4"]
    p = json.loads((ROOT / "analysis/t052-b0/predicado.json").read_text())
    assert p["ram_byte_10"] == 0
    assert p["ram_equals_nvram_first_100"] is True
    assert p["block_id"] == "0xbc0005"
    assert p["nvram_unique_sha256_100"] == [NVRAM_BLOCK_SHA]
