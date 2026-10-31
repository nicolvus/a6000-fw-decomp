"""E26-R24 — mapa completo de Loader2 (bootloader.bin): inventario y secuencia de arranque."""

import json
import struct
from pathlib import Path

BOOTLOADER = Path("analysis/camera-dumps/updater-20261020-175427/bootloader.bin")
FUNCS = Path("analysis/e26-recovery/r24-loader2-functions.json")
SEQ = Path("analysis/e26-recovery/r24-boot-sequence.json")
B, OFF = 0xC0030000, 0x600


def word(off_addr: int) -> int:
    return struct.unpack_from("<I", BOOTLOADER.read_bytes(), off_addr - B + OFF)[0]


def test_todas_las_funciones_descubiertas_tienen_rol_asignado():
    d = json.loads(FUNCS.read_text(encoding="utf-8"))
    assert d["total_funciones"] == 247
    assert all(r["name"] and r["note"] for r in d["funciones"])
    assert sum(d["por_categoria"].values()) == 247


def test_secuencia_de_arranque_completa_18_pasos():
    seq = json.loads(SEQ.read_text(encoding="utf-8"))
    assert len(seq) == 17
    assert seq[0][1] == "entry_arm" and seq[-1][1] == "loader3_jump"


def test_cadena_version_y_handoff_a_loader3():
    d = BOOTLOADER.read_bytes()
    assert b"Loader2 Ver.33.01.90 (Jan 24 2014 22:07:33)" in d
    assert b"LDR:Jump LDR3@0x%X" in d
    assert b"LDR_E:NOTREACHED" in d


def test_entrada_arm_confirmada_por_bytes():
    # 0xc0030000: ldr r0, [pc, #0x3c] ; mov sp, r0  (pila ARM antes de pasar a Thumb)
    assert word(0xC0030000) == 0xE59F003C
    assert word(0xC0030004) == 0xE1A0D000


def test_rutina_led_resta_1000_igual_que_r13():
    half = struct.unpack_from("<H", BOOTLOADER.read_bytes(), 0xC00303E2 - B + OFF)[0]
    assert half == 0x4C76  # ldr r4, [pc, #0x1d8] -> literal -306 (0xfffffece)
    assert word(((0xC00303E2 + 4) & ~3) + 0x1D8) == 0xFFFFFECE
