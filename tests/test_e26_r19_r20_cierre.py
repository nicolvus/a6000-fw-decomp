"""Cierre estático de E26-R19-USB-EVT13 y E26-R20-GPIO4 (bytes del BootROM y de Darwin)."""

import itertools
import struct
from pathlib import Path

import pytest

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin")
DARWIN = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
)
ROM_BASE, DARWIN_BASE = 0xFFFF0000, 0x4200


def rom_words(addr: int, n: int) -> tuple[int, ...]:
    return struct.unpack_from(f"<{n}I", ROM.read_bytes(), addr - ROM_BASE)


def test_tablas_de_muestreo_serie_del_bootrom():
    """`0x554` elige entre dos tablas de 11 instantes de muestreo (inicio+8+paridad+parada)."""
    lento = rom_words(0xFFFF19F0, 11)
    rapido = rom_words(0xFFFF1A1C, 11)
    assert {b - a for a, b in itertools.pairwise(lento)} == {250}
    assert {b - a for a, b in itertools.pairwise(rapido)} == {84}
    assert (lento[0], rapido[0]) == (100, 28)


@pytest.mark.skipif(not DARWIN.exists(), reason="darwin_core.bin ausente")
def test_aviso_post_0x13_es_registro_de_traza():
    """El callback [0xc] llama `post(0x13,…)` (`0xeb30`); éste solo copia registros a anillos de traza."""
    d = DARWIN.read_bytes()
    cb = 0x106C0 - DARWIN_BASE
    assert (
        struct.unpack_from("<H", d, 0x10708 - DARWIN_BASE)[0] == 0x2013
    )  # movs r0,#0x13
    # `[0x20002dbc]` solo aparece en el literal del módulo USB (0x1093c).
    lits = [
        i + DARWIN_BASE
        for i in range(0, len(d) - 3, 4)
        if d[i : i + 4] == struct.pack("<I", 0x20002DBC)
    ]
    assert lits == [0x1093C] and cb > 0


@pytest.mark.skipif(not DARWIN.exists(), reason="darwin_core.bin ausente")
def test_un_solo_endpoint_interrupt_in():
    d = DARWIN.read_bytes()
    o = 0x239E4
    assert d[o + 0x2D : o + 0x34] == bytes([7, 5, 0x81, 3, 8, 0, 1])  # EP1 IN interrupt
    assert d.count(bytes([7, 5]), o, o + 0x100) == 1


def test_bit1_de_moderreg_es_boot_serial_in_en_el_codigo_sony():
    base = Path(
        "analysis/session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014"
    )
    misc = (base / "include/mach/regs-misc.h").read_text(encoding="utf-8")
    assert "MISC_MODEREG_BOOT_SERIAL_IN\t0x0002" in misc
    assert "TMCK_1MHZ\t\t\tTMCK_DIV4" in (base / "hwtimer.c").read_text(
        encoding="utf-8"
    )


def test_receptor_serie_8_datos_y_paridad_impar():
    rom = ROM.read_bytes()
    half = lambda a: struct.unpack_from("<H", rom, a - ROM_BASE)[0]
    assert half(0xFFFF06D0) == 0x2C08  # cmp r4,#8: ocho bits de datos
    assert (half(0xFFFF06E2), half(0xFFFF06EA)) == (
        0x2E01,
        0x2501,
    )  # cmp r6,#1 ; movs r5,#1 (si XOR != 1)
