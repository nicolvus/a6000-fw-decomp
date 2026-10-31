"""E26-R40 — JTAG/SWD del BIONZ: ausencia de bloqueo por software, DAP CoreSight y bucle de LED sin apagado.

Leen el manual GPL de Sony (`analysis/session18`), binarios de `bootloader.bin`/`bootrom.bin` y el
kernel del actualizador; se omiten si faltan.  Nada toca la cámara.
"""

import io
import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "references/fwtool"), str(ROOT / "scripts")]

GPL = ROOT / "analysis/session18/codex-g/oss-linux/linux"
UPD = ROOT / "analysis/camera-dumps/updater-20261020-175427"
NAND = ROOT / "analysis/camera-dumps/nand-20261020"
L3 = 0xC01F0000

DAP_BASE = 0xF2710000
DAP_CTI_UNLOCK = 0xC5ACCE55


def _need(*paths: Path) -> None:
    for p in paths:
        if not p.exists():
            pytest.skip(f"falta {p.relative_to(ROOT)} (no versionado)")


def _lits(data: bytes, lo: int, hi: int) -> set[int]:
    return {
        v
        for i in range(0, len(data) - 3, 2)
        if lo <= (v := struct.unpack_from("<I", data, i)[0]) < hi
    }


def test_dap_coresight_en_el_arbol_gpl_de_sony():
    _need(GPL / "arch/arm/mach-cxd90014/include/mach/regs-dap.h")
    plat = (GPL / "arch/arm/mach-cxd90014/include/mach/platform.h").read_text()
    regs = (GPL / "arch/arm/mach-cxd90014/include/mach/regs-dap.h").read_text()
    assert "#define CXD90014_DAP_BASE\t0xf2710000" in plat
    assert "#define   DAP_CTI_UNLOCK  0xc5acce55" in regs
    dap_c = (GPL / "arch/arm/mach-cxd90014/dap.c").read_text()
    # el único uso de CoreSight en el GPL de Sony: desenmascarar la IRQ de la PMU por canal CTI
    assert "writel_relaxed(DAP_CTI_UNLOCK, VA_DAPCTI(id)+DAP_CTILOCK)" in dap_c
    assert "DAP_CTICH_PMUIRQ" in dap_c


def test_configs_ice_arrancan_bajo_depurador_sin_desactivar_el_dap():
    base = GPL / "arch/arm/configs/cxd90014_set_defconfig"
    ice = GPL / "arch/arm/configs/cxd90014_ice_initrd_defconfig"
    _need(base, ice)
    b, i = base.read_text(), ice.read_text()
    assert "CONFIG_ARM_DAP=y" in b
    # "ice" (in-circuit emulator) carga kernel+initrd por direcciones fijas, no por nflasha1
    assert "initrd=0x81000000,0x1400000" in i
    assert "root=/dev/ram0" in i


def test_ningun_cargador_toca_el_dap_antes_de_linux():
    _need(UPD / "bootrom.bin", UPD / "bootloader.bin")
    rom = (UPD / "bootrom.bin").read_bytes()
    bl = (UPD / "bootloader.bin").read_bytes()
    assert not _lits(rom, DAP_BASE, DAP_BASE + 0x10000)
    assert not _lits(bl[0x600:0x7200], DAP_BASE, DAP_BASE + 0x10000)  # Loader2
    assert not _lits(bl[0x22800:0x38000], DAP_BASE, DAP_BASE + 0x10000)  # Loader3
    assert not _lits(bl[0x18800:0x1C000], DAP_BASE, DAP_BASE + 0x10000)  # ARM7


def test_kernel_del_actualizador_solo_usa_el_dap_para_cti_de_la_pmu():
    from fwtool.archive.fat import readFat  # type: ignore[import-not-found]

    _need(NAND / "dev_nflasha1.bin")
    img = (NAND / "dev_nflasha1.bin").read_bytes()
    vmlinux = next(
        f.contents.read()
        for f in readFat(io.BytesIO(img))
        if f.path == "/boot/vmlinux.bin"
    )
    z = vmlinux[vmlinux.find(b"\x1f\x8b\x08") :]
    k = zlib.decompressobj(31).decompress(z)
    hits = _lits(k, DAP_BASE, DAP_BASE + 0x10000)
    # DAP_CTI(0) = 0x8000 (N_DAP_CTI=4, paso 0x1000); CTIINTACK=+0x10, CTIGATE=+0x140, CTILOCK=+0xfb0
    cti0 = {DAP_BASE + 0x8000 + off for off in (0x10, 0x140, 0xFB0)}
    assert (
        cti0 <= hits
    )  # los tres literales de dap.c están, aunque el barrido ciego halle más


def test_dap_cti_lock_unico_literal_0xc5acce55_en_el_kernel():
    from fwtool.archive.fat import readFat  # type: ignore[import-not-found]

    _need(NAND / "dev_nflasha1.bin")
    img = (NAND / "dev_nflasha1.bin").read_bytes()
    vmlinux = next(
        f.contents.read()
        for f in readFat(io.BytesIO(img))
        if f.path == "/boot/vmlinux.bin"
    )
    z = vmlinux[vmlinux.find(b"\x1f\x8b\x08") :]
    k = zlib.decompressobj(31).decompress(z)
    # el valor de desbloqueo del CTI aparece una sola vez: solo dap.c lo usa (ningún otro subsistema)
    assert k.count(struct.pack("<I", DAP_CTI_UNLOCK)) == 1


def test_bucle_de_led_tras_302_no_apaga_la_cpu():
    _need(UPD / "bootloader.bin")
    l3 = (UPD / "bootloader.bin").read_bytes()[0x22800:0x38000]
    # c01f3bf6: b #0xc01f3bc8 — salto incondicional hacia atrás, sin wfi/poweroff
    assert l3[0xC01F3BF6 - L3 : 0xC01F3BF8 - L3].hex() == "e7e7"


def test_llamadores_de_chk_updater():
    """`c01f159a` (chk_updater) tiene 8 llamadores `bl`, incluidos los dos de la elección de modo."""
    _need(UPD / "bootloader.bin")
    l3 = (UPD / "bootloader.bin").read_bytes()[0x22800:0x38000]
    sites = {
        0xC01F11A8: "00f0f7f9",
        0xC01F1DF8: "fff7cffb",
        0xC01F1E10: "fff7c3fb",  # elección de modo 3 (c01f1e14: cbz r0 -> movs r0,#3)
        0xC01F2122: "fff73afa",  # segunda comprobación, antes de Sync mode
        0xC01F75CC: "f9f7e5ff",
        0xC01F7748: "f9f727ff",
        0xC01F8E24: "f8f7b9fb",
        0xC01F8E76: "f8f790fb",
    }
    for addr, expected in sites.items():
        off = addr - L3
        assert l3[off : off + 4].hex() == expected, hex(addr)
    # c01f1e14: cbz r0,#0xc01f1e1a; movs r0,#3 -> UPDATER solo si chk_updater devuelve != 0
    assert l3[0xC01F1E14 - L3 : 0xC01F1E18 - L3].hex() == "08b10320"


def test_swd_en_el_manual_de_servicio_y_r4911_r4912_sin_montar():
    manual = ROOT / "references/manuals/a6000_service_L3.txt"
    _need(manual)
    text = manual.read_text(errors="replace")
    assert "Serial Wire Debug" in text
    assert "SWCLK" in text and "SWDIO" in text
    # JTAG convencional del BIONZ: TDI/TCK/TMS atados a alimentación (D_3.15V_MSS)
    idx = text.find("D_3.15V_MSS")
    assert idx != -1
