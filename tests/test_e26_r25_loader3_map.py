"""E26-R25 — mapa completo de Loader3 (bootloader.bin, 0xc01f0000..0xc0205800): inventario y entrada."""

import json
import struct
from pathlib import Path

BOOTLOADER = Path("analysis/camera-dumps/updater-20261020-175427/bootloader.bin")
FUNCS = Path("analysis/e26-recovery/r25-loader3-functions.json")
SEQ = Path("analysis/e26-recovery/r25-boot-sequence.json")
B, OFF = 0xC01F0000, 0x22800


def word(addr: int) -> int:
    return struct.unpack_from("<I", BOOTLOADER.read_bytes(), addr - B + OFF)[0]


def test_todas_las_funciones_descubiertas_tienen_rol_asignado():
    d = json.loads(FUNCS.read_text(encoding="utf-8"))
    assert d["total_funciones"] == 674
    assert all(r["name"] and r["note"] for r in d["funciones"])
    assert sum(d["por_categoria"].values()) == 674


def test_secuencia_de_entrada_y_despacho():
    seq = json.loads(SEQ.read_text(encoding="utf-8"))
    assert seq[0][1] == "exc_vectors" and seq[-1][1] == "led_error_blink"
    assert any(p[1] == "boot_dispatch" for p in seq)


def test_vector_de_reset_salta_a_entry_arm_y_el_resto_al_led():
    # 0xc01f0000: b 0xc01f0028 (reset); 0xc01f0004..1c: b 0xc01f0020 (excepciones -> LED)
    assert word(0xC01F0000) == 0xEA000008  # b #0x28 (reset)
    assert word(0xC01F0004) == 0xEA000005  # b #0x20 (excepción)


def test_cadenas_de_registro_de_las_cuatro_capas():
    d = BOOTLOADER.read_bytes()
    for tag in (b"LD3:", b"LD3_E:", b"BOS_E:", b"CFG_E:", b"FAT_E:"):
        assert tag in d


def test_numero_de_cadenas_con_rol_asignado_coincide_con_lo_hallado():
    d = json.loads(FUNCS.read_text(encoding="utf-8"))
    assert d["por_categoria"]["log"] == 30
    assert d["por_categoria"]["fat"] == 6  # ligadas por informe (R13 P1-P7)
