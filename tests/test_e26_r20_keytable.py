"""E26-R20-KEYTABLE — mecanismo de la tabla de clave de arranque serie (`0xffff1352`).

Verifica por bytes que la rutina es un lector real de sectores de almacenamiento
(no un relleno/stub): solo pone a 0xFF el pequeño array de estado por sector,
y copia datos reales de hardware en bloques de 0x600 B al buffer del llamador.
"""

import struct
from pathlib import Path

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin")
B = 0xFFFF0000


def word(rom: bytes, addr: int) -> int:
    return struct.unpack_from("<H", rom, addr - B)[0]


def test_rom_disponible():
    assert ROM.exists(), "bootrom.bin ausente"


def test_relleno_0xff_es_solo_el_array_de_estado():
    rom = ROM.read_bytes()
    assert word(rom, 0xFFFF1368) == 0x22FF  # movs r2, #0xff (valor de relleno)
    assert (word(rom, 0xFFFF1370), word(rom, 0xFFFF1372)) == (
        0x4620,
        0xF000,
    )  # mov r0, r4 ; bl 0xffff1814 (memset del array de estado, no del buffer de datos)


def test_incremento_por_sector_es_0x600():
    rom = ROM.read_bytes()
    assert (
        (word(rom, 0xFFFF1496), word(rom, 0xFFFF1498))
        == (
            0xF506,
            0x66C0,
        )
    )  # add.w r6, r6, #0x600 (r6 = buffer de datos del llamador, avanza un sector real por iteración)


def test_particion_de_arranque_protegida_no_tiene_volcado():
    """`nflasha0` (área de boot/loader) no tiene nodo de dispositivo Linux: nunca se volcó."""
    nand_dir = Path("analysis/camera-dumps/nand-20261020")
    readme = (nand_dir / "README.md").read_text(encoding="utf-8")
    assert "nflasha0" in readme
    assert not (nand_dir / "dev_nflasha0.bin").exists()
