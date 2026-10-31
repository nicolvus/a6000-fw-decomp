"""E26-R33: veracidad de «la clave serie está en `nflasha0`» contra los bytes del BootROM."""

import struct
import zlib
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin").read_bytes()
BASE = 0xFFFF0000


def b(a: int, n: int) -> bytes:
    return ROM[a - BASE : a - BASE + n]


def lit(a: int) -> int:
    return struct.unpack_from("<I", ROM, a - BASE)[0]


def test_tabla_es_el_tercer_sector_de_la_cabecera_leida_del_bloque_0():
    assert (lit(0xFFFF054C), lit(0xFFFF0550)) == (0xC0000600, 0xC0001200)
    assert 0xC0001200 - 0xC0000600 == 2 * 0x600
    assert b(0xFFFF0336, 2) + b(0xFFFF033A, 2) == bytes.fromhex(
        "00260324"
    )  # bloque 0, 3 sectores


def test_find_key_solo_exige_una_palabra_no_borrada_y_copia_las_dos_primeras():
    assert b(0xFFFF03AE, 6) == bytes.fromhex(
        "54f82100401c"
    )  # ldr.w r0,[r4,r1,lsl#2]; adds r0,#1
    assert b(0xFFFF03CC, 4) == bytes.fromhex("b1f5c07f")  # cmp.w r1,#0x180 (0x600 B)
    assert b(0xFFFF03B6, 2) + b(0xFFFF03BC, 2) == bytes.fromhex(
        "28686868"
    )  # [r5], [r5+4]


def test_main_sigue_cuando_storage_init_y_load_header_devuelven_0():
    """Corrige R23 §1: `cbz` salta *sobre* `serial_entry` con r0 == 0."""
    assert b(0xFFFF110E, 2) == bytes.fromhex("28b1")  # cbz r0,0x111c
    assert b(0xFFFF1120, 2) == bytes.fromhex("28b1")  # cbz r0,0x112e


def test_load_header_devuelve_0_ante_errores_distintos_de_3005_3006():
    """R12 §3 vigente: cualquier otro error cae en el `movs r0,#0` de 0x376."""
    assert b(0xFFFF0362, 12) == bytes.fromhex("a4f54050053808d001280ed0")
    assert b(0xFFFF0376, 2) == bytes.fromhex("0020")


def test_sin_clave_y_sin_serie_no_hay_arranque():
    # receptor: sin flanco -> 0x3002, que sale como 0x3001
    assert b(0xFFFF08D8, 4) == bytes.fromhex("43f20200")
    assert b(0xFFFF0910, 6) + b(0xFFFF093E, 4) == bytes.fromhex("a0f54051023943f20104")
    # serial_entry: 0x3001 -> LED 0x1001
    assert b(0xFFFF1008, 6) + b(0xFFFF1018, 4) == bytes.fromhex("43f20100844241f20104")


def crc_rom(data: bytes) -> int:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, 0x8000)
    mu.mem_write(BASE, ROM)
    mu.mem_map(0xC0000000, 0x10000)
    mu.mem_write(0xC0000000, data)
    mu.reg_write(UC_ARM_REG_R0, 0xC0000000)
    mu.reg_write(UC_ARM_REG_R1, len(data))
    mu.reg_write(UC_ARM_REG_SP, 0xC000F000)
    mu.reg_write(UC_ARM_REG_LR, 0xFFFF7000 | 1)
    mu.emu_start(0xFFFF0C52 | 1, 0xFFFF7000)
    return mu.reg_read(UC_ARM_REG_R0)


def test_entrada_valida_es_clave_mas_crc32_complementado():
    k = struct.pack("<I", 0x12345678)
    ok = struct.pack("<I", zlib.crc32(k) ^ 0xFFFFFFFF)
    assert crc_rom(k + ok) == 0xFFFFFFFF  # main 0x11ae: aceptada si devuelve -1
    assert crc_rom(k + struct.pack("<I", zlib.crc32(k))) != 0xFFFFFFFF
    assert crc_rom(b"\xff" * 8) != 0xFFFFFFFF
