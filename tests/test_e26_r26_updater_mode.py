"""E26-R26 — gate de `\\updater\\mode` en la selección de arranque y descarte de la clave PwrIC."""

import struct
from pathlib import Path

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootloader.bin")
B, OFF = 0xC01F0000, 0x22800


def half(addr: int) -> int:
    return struct.unpack_from("<H", ROM.read_bytes(), addr - B + OFF)[0]


def test_tabla_tbb_de_boot_dispatch_separa_cadena_especial():
    d = ROM.read_bytes()
    tbl = d[0xC01F1224 - B + OFF : 0xC01F1224 - B + OFF + 15]
    assert tbl == bytes.fromhex(
        "24 08 08 08 08 08 08 13 13 13 08 08 08 13 13".replace(" ", "")
    )
    base = 0xC01F1224
    modos_especiales = {i for i, b in enumerate(tbl) if b != tbl[1] and i != 0}
    assert modos_especiales == {7, 8, 9, 13, 14}
    assert {base + 2 * tbl[i] for i in modos_especiales} == {0xC01F124A}


def test_cadena_updater_mode_referenciada_y_gate_fuerza_modo_normal():
    d = ROM.read_bytes()
    t = ((0xC01F15BA + 4) & ~3) + 0x3E8
    assert d[t - B + OFF : t - B + OFF + 13] == b"\\updater\\mode"
    assert half(0xC01F1DFC) == 0x2800  # cmp r0,#0 (resultado de chk_updater)
    assert half(0xC01F1E14) == 0xB108  # cbz r0,#0xc01f1e1a
    assert (
        half(0xC01F1E16) == 0x2003
    )  # movs r0,#3 (fuerza modo normal si falta el archivo)


def test_clave_ld3_key_es_de_pwric_no_de_almacenamiento():
    assert half(0xC01F0594) == 0x2803  # cmp r0,#3: solo tipos de PwrIC conocidos
    # la función gate (0xc01f5ba6) referencia 0xc00e0060 (PwrIC), nunca 0xc0001200 (tabla BootROM)
    assert ROM.read_bytes().find(b"PWR:inv PwrIC") >= 0
