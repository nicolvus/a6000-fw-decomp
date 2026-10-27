"""E24-01: comprobaciones reproducibles del arranque y del modo actualizador.

Leen binarios locales no versionados (volcado NAND, BootROM, firmware oficial);
se omiten si faltan. Informe: docs/capture/e24-01-arranque-recuperacion.md.
"""
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NAND = ROOT / "analysis/camera-dumps/nand-20261020"
BOOTROM = ROOT / "analysis/camera-dumps/nvram-referencia-20261020-214913/bootrom.bin"
DARWIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0640_darwin/darwin_core.bin"
DARWIN_BASE = 0x4200
BOOTROM_BASE = 0xFFFF0000


def _need(path: Path) -> bytes:
    if not path.exists():
        pytest.skip(f"falta {path.relative_to(ROOT)}")
    return path.read_bytes()


def _u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def _thumb_lit(data: bytes, base: int, insn_addr: int, imm: int) -> int:
    """Valor de un `ldr rX, [pc, #imm]` Thumb."""
    return _u32(data, ((insn_addr + 4) & ~3) + imm - base)


@pytest.fixture(scope="module")
def updater_root(tmp_path_factory) -> Path:
    img = NAND / "dev_nflasha1.bin"
    _need(img)
    if not (shutil.which("mcopy") and shutil.which("7z")):
        pytest.skip("faltan mtools/7z")
    out = tmp_path_factory.mktemp("nflasha1")
    subprocess.run(["mcopy", "-s", "-n", "-i", str(img), "::boot", "::p1chksum", str(out)], check=True)
    # 7z devuelve 2 por los nodos de /dev del cramfs; basta con que extraiga los archivos
    subprocess.run(["7z", "x", "-y", f"-o{out / 'initrd'}", str(out / "boot/initrd.img")],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert (out / "initrd/sbin/init").is_file()
    return out


def test_nand_partition_table_and_windows():
    full = NAND / "dev_nflasha.bin"
    _need(full)
    with full.open("rb") as f:
        head = f.read(0x200)
        assert head[:8] == b"82461.00"  # tabla de particiones en los primeros 0x40000
        f.seek(0x40000)
        assert f.read(0x1000) == (NAND / "dev_nflasha1.bin").read_bytes()[:0x1000]
    assert (NAND / "dev_nflasha3.bin").read_bytes()[:4] == b"TPZL"
    assert (NAND / "dev_nflasha5.bin").read_bytes()[:4] == b"WBI1"


def test_nflasha1_is_updater_kernel(updater_root):
    assert (updater_root / "boot/loadaddr.txt").read_text().strip() == "0x81528000,0x80628000"
    assert (updater_root / "boot/vmlinux.bin").read_bytes()[0x24:0x28] == b"\x18\x28\x6f\x01"  # zImage
    assert (updater_root / "initrd/version.txt").read_text().strip() == "41.01.28"


def test_updater_init_ignores_darwin_result(updater_root):
    init = (updater_root / "initrd/sbin/init").read_text()
    darwin = init.index("us_darwin_init.sh")
    usb = init.index("UdtrMain.sh &")
    assert darwin < usb  # Darwin se intenta antes de lanzar la parte USB
    assert "$?" not in init[darwin:usb].split("fi", 1)[0]  # sin comprobar el resultado
    script = (updater_root / "initrd/usr/bin/us_darwin_init.sh").read_text()
    assert "ud_darwin_init.elf\n" in script and script.rstrip().endswith("exit 0")


def test_ud_darwin_init_is_bounded(updater_root):
    elf = (updater_root / "initrd/usr/bin/ud_darwin_init.elf").read_bytes()
    def lit(addr: int) -> int:
        return _u32(elf, addr - 0x8000)  # PT_LOAD en 0x8000

    assert [lit(a) for a in (0x8CF0, 0x8CF4, 0x8CF8)] == [0xF900D4, 0xF900B1, 0xF9006D]  # ids Backup
    assert lit(0x8D08) == 0xF2910000  # GPIO mapeado por /dev/mem
    assert lit(0x8E58) == 29_999_999  # límite del bucle de reintentos


def test_power_ic_type_comes_from_backup(updater_root):
    lib = (updater_root / "initrd/usr/lib/libupdaterufunc.so").read_bytes()
    assert _u32(lib, 0x864) == 0x00510001  # Backup_read(0x510001) en get_power_IC_type


def test_bootrom_is_loader1_without_darwin_link():
    rom = _need(BOOTROM)
    assert b"Musashi Loader1 Ver.01.00" in rom
    assert _thumb_lit(rom, BOOTROM_BASE, 0xFFFF1094, 0x228) == 0xF2915000
    assert _thumb_lit(rom, BOOTROM_BASE, 0xFFFF10EA, 0x1D8) == 0xF2910410  # bit 22: rama 0xffff0fa0
    assert b"Loader boot failed" in rom


def test_darwin_core_drives_system_rails():
    capstone = pytest.importorskip("capstone")
    core = _need(DARWIN)
    assert _u32(core, 0x55A0 - DARWIN_BASE) == 0x42668000  # base bit-band PDOR usada por 0x51c0
    # tabla de la secuencia de encendido (manejador Thumb, bandera)
    table = {0x28C74: 0x1578D, 0x28C9C: 0x157C5, 0x28CB4: 0x157A9}
    assert all(_u32(core, a - DARWIN_BASE) == v for a, v in table.items())
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    for start, pin in ((0x1579A, 0x130), (0x157B6, 0x20C), (0x157D2, 0x210)):  # DD_ON1/2/3
        ins = list(md.disasm(core[start - DARWIN_BASE:start - DARWIN_BASE + 10], start))
        assert ins[0].op_str == "r1, #1"
        assert ins[1].op_str == f"r0, #{pin:#x}"
        assert ins[2].mnemonic == "bl" and ins[2].op_str == "#0x51c0"
