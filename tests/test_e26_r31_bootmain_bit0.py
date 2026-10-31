"""E26-R31: cierre estático de `MODEREG` bit 0 = `BOOT_MAIN` (CL1000) por exclusión de consumidores."""

import struct
from pathlib import Path

import pytest

ROM = Path("analysis/camera-dumps/updater-20261020-175427/bootrom.bin")
LOADER = Path("analysis/camera-dumps/updater-20261020-175427/bootloader.bin")
MCMN = Path(
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/kmod/mcmn_drv.ko"
)
OSS = Path("analysis/session18/main/sony-oss-extracted/linux/arch/arm")
SCHEM = Path("references/manuals")


def words(path: Path, value: int) -> list[int]:
    d = path.read_bytes()
    return [
        i for i in range(0, len(d) - 3, 2) if struct.unpack_from("<I", d, i)[0] == value
    ]


def test_loader3_solo_registra_moderreg_en_bruto():
    """Loader3 (archivo `0x22800` = `0xc01f0000`) lee `[MISC+0x10]` una vez y lo pasa al registro, sin probar bits."""
    b = LOADER.read_bytes()
    assert words(LOADER, 0xF2915000) == [0x27768]  # único literal de la base MISC
    assert struct.unpack_from("<H", b, 0x2772A)[0] == 0x6920  # ldr r0,[r4,#0x10]
    assert (
        struct.unpack_from("<H", b, 0x27730)[0] == 0x9000
    )  # str r0,[sp] -> argumento del log
    assert words(LOADER, 0xF2915010) == []


@pytest.mark.skipif(not MCMN.exists(), reason="mcmn_drv.ko ausente")
def test_mcmn_usa_moderead_para_deteccion_de_tarjetas():
    """`MODEREAD` (= `MODEREG`) bit 16 = MSX_INS_HIZ, bits 24/26 = CD MMC, bits 25/27 = WP MMC."""
    d = MCMN.read_bytes()
    word = lambda o: struct.unpack_from("<I", d, o)[0]
    assert word(0x70C) == 0xE7E03853  # ubfx r3,r3,#16,#1 (getmsindata)
    assert (word(0x56C), word(0x574)) == (
        0xE3A06019,
        0xE3A0601B,
    )  # mov r6,#25/#27 (getmmcwpdata)
    assert (word(0x868), word(0x870)) == (
        0xE3A06018,
        0xE3A0601A,
    )  # mov r6,#24/#26 (getmmccddata)
    assert b"<getmsindata> MSX_INS_HIZ(bit:%d)" in d and b"MODEREAD(0x%08X)" in d


def test_oss_sony_boot_mode_en_bits_bajos():
    m4132 = (OSS / "mach-cxd4132/include/mach/regs-misc.h").read_text(encoding="utf-8")
    m90014 = (OSS / "mach-cxd90014/include/mach/regs-misc.h").read_text(
        encoding="utf-8"
    )
    assert (
        "MODEREAD_BM1\t\t0x00000002" in m4132 and "DDRCKSEL_MASK\t\t0x01000000" in m4132
    )
    assert "MISC_MODEREG_BOOT_SERIAL_IN\t0x0002" in m90014


def test_bloque_boot_del_esquema_tiene_tres_redes():
    for f in ("a6000_service_L3.txt", "a6300_service_L3.txt"):
        t = (SCHEM / f).read_text(encoding="utf-8", errors="replace")
        assert all(n in t for n in ("DDRCKSEL", "BOOT_SERIAL_IN", "BOOT_MAIN"))
    assert "CL1000" in (SCHEM / "a6000_service_L3.txt").read_text(
        encoding="utf-8", errors="replace"
    )


def test_bootrom_solo_lee_moderreg_desde_dos_sitios():
    """Literal de la base MISC solo en `0x968` (receptor, bit 1) y `0x12c0` (selector `main`, bit 0)."""
    assert words(ROM, 0xF2915000) == [0x968, 0x12C0]
