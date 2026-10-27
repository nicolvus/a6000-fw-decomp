"""E24-03: auditoría offline de respaldos y del FDAT de recuperación 3.23.

Lee binarios locales no versionados (firmware, volcados, FDAT); se omiten si faltan.
No toca la cámara. Informe: docs/capture/e24-03-auditoria-recuperacion-usb.md.
"""
import hashlib
import io
import shutil
import subprocess
import sys
import tarfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DUMPS = ROOT / "analysis/camera-dumps"
NAND = DUMPS / "nand-20261020"
REF = DUMPS / "nvram-referencia-20261020-214913"
PRE_T024 = DUMPS / "20261026-232912-pre-T024-darwin-tipo0"
FW321 = ROOT / "firmware/extracted/fw321"
OFFICIAL_DAT = (ROOT / "firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app"
                / "Contents/Resources/FirmwareData_ILCE6000V321.dat")
PATCH = ROOT / "analysis/darwin-patch"
REC = PATCH / "fdat/recuperacion-323"
TIPO0_FDAT = PATCH / "fdat/firmware_packed.dat"

OFFICIAL_CORE = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
TIPO0_CORE = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
OFFICIAL_TAR = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
OFFICIAL_UPDATER = "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
OFFICIAL_FDAT = "603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90"
REC_DAT = "5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf"
REC_FDAT = "cfb65c8aad8ac8a3ccb1c4c758d485feee1ebf2e83e503d9c62d59fb96b01ce4"
BOOTROM = "81a17e039a2debfe589b127e12384ed4d7c2ba0d0c819238d0b021b466246026"


def _need(*paths: Path) -> None:
    for p in paths:
        if not p.exists():
            pytest.skip(f"falta {p.relative_to(ROOT)}")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_sums(folder: Path, only: set[str] | None = None) -> None:
    """Comprueba SHA256SUMS ignorando la línea que se lista a sí misma."""
    for line in (folder / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(None, 1)
        if name == "SHA256SUMS" or (only and name not in only):
            continue
        assert _sha(folder / name) == digest, f"{folder.name}/{name}"


@pytest.fixture(scope="module")
def fwtool():
    _need(ROOT / "references/fwtool/fwtool/sony/fdat.py")
    sys.path.insert(0, str(ROOT / "references/fwtool"))
    pytest.importorskip("Cryptodome")
    from fwtool.sony import dat, fdat  # type: ignore[import-not-found]
    return dat, fdat


def _open_dat(fwtool, path: Path):
    """Descifra un .dat y devuelve (cabecera del contenedor, FDAT en claro ya parseado, firmware.tar)."""
    dat, fdat = fwtool
    _need(path)
    with path.open("rb") as f:
        container = dat.readDat(f)  # comprueba magia y CRC de DEND
        _, plain = fdat.decryptFdat(container.firmwareData)  # comprueba suma y bandera final de cada bloque
        buf = io.BytesIO()
        shutil.copyfileobj(plain, buf)
    buf.seek(0)
    parsed = fdat.readFdat(buf)  # comprueba magia y CRC-32 de cabecera
    parsed.firmware.seek(0)
    parsed.fs.seek(0)
    return container, parsed, parsed.firmware.read(), parsed.fs.read()  # FilePart de fwtool, sin tipos


def _members(tar_bytes: bytes) -> dict[str, bytes]:
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        return {m.name: tf.extractfile(m).read() for m in tf.getmembers() if m.isfile()}  # type: ignore[union-attr]


@pytest.fixture(scope="module")
def rec(fwtool):
    return _open_dat(fwtool, REC / "firmware_packed.dat")


def test_nvram_backups_intact():
    _need(REF / "SHA256SUMS", PRE_T024 / "SHA256SUMS")
    for folder in (REF, PRE_T024):
        _verify_sums(folder)
        assert _sha(folder / "bootrom.bin") == BOOTROM
        assert (folder / "backup_flash.bin").stat().st_size == 852647
        assert b"3.21" in (folder / "info.txt").read_bytes()


def test_nand_dump_partitions_intact():
    _need(NAND / "SHA256SUMS")
    _verify_sums(NAND, {"dev_nflasha1.bin", "dev_nflasha2.bin", "dev_nflasha.bin"})
    assert (NAND / "dev_nflasha1.bin").stat().st_size == 6291456


def test_official_dat_matches_extracted_fdat(fwtool):
    _, parsed, tar_bytes, fs = _open_dat(fwtool, OFFICIAL_DAT)
    assert (parsed.model, parsed.region, parsed.version) == (0x41030035, 0, "3.21")
    assert hashlib.sha256(tar_bytes).hexdigest() == OFFICIAL_TAR
    assert hashlib.sha256(fs).hexdigest() == OFFICIAL_UPDATER
    assert _sha(FW321 / "firmware.fdat") == OFFICIAL_FDAT


def test_recovery_323_identity(rec):
    container, parsed, tar_bytes, fs = rec
    assert (parsed.model, parsed.region, parsed.version, parsed.isAccessory) == (0x41030035, 0, "3.23", False)
    assert container.updaterUsbDescriptors == [(0x54C, 0x3E2)] and not container.isLens
    assert _sha(REC / "firmware_packed.dat") == REC_DAT and _sha(REC / "firmware_packed.fdat") == REC_FDAT
    assert hashlib.sha256(tar_bytes).hexdigest() == OFFICIAL_TAR  # el tar completo es el oficial
    assert hashlib.sha256(fs).hexdigest() == OFFICIAL_UPDATER


def test_recovery_323_ships_original_darwin_not_type0(rec):
    files = _members(rec[2])
    core, total = files["0640_darwin/darwin_core.bin"], files["0641_darwin_sum/darwin.sum"]
    assert hashlib.sha256(core).hexdigest() == OFFICIAL_CORE != TIPO0_CORE
    assert f"{zlib.crc32(core):08x}" == "9ff7148c"
    assert total.decode().split(",")[:3] == ["0", "9ff7148c", f"{len(core):08x}"]  # CRC-32 y tamaño de darwin.sum
    assert not [n for n in files if "darwin_boo" in n or "loader" in n.lower()]
    assert b"VER0.78" in core


def test_type0_fdat_differs_only_in_darwin(fwtool):
    _, parsed, tar_bytes, _ = _open_dat(fwtool, TIPO0_FDAT)
    assert parsed.version == "3.22"
    rec_files = _members(_open_dat(fwtool, REC / "firmware_packed.dat")[2])
    t0 = _members(tar_bytes)
    assert {n for n in t0 if t0[n] != rec_files[n]} == {"0640_darwin/darwin_core.bin", "0641_darwin_sum/darwin.sum"}
    assert hashlib.sha256(t0["0640_darwin/darwin_core.bin"]).hexdigest() == TIPO0_CORE
    assert b"VER0.78" in t0["0640_darwin/darwin_core.bin"]  # misma cadena de versión: no la distingue


def test_recovery_323_rebuilds_byte_for_byte(tmp_path):
    _need(REC / "config-323.yaml", FW321 / "firmware.tar", FW321 / "updater.img")
    subprocess.run([sys.executable, str(ROOT / "references/fwtool/fwtool.py"), "pack", "-c", str(REC / "config-323.yaml"),
                    "-u", str(FW321 / "updater.img"), "-f", str(FW321 / "firmware.tar"), "-o", str(tmp_path)],
                   check=True, capture_output=True)
    assert _sha(tmp_path / "firmware_packed.dat") == REC_DAT
    assert _sha(tmp_path / "firmware_packed.fdat") == REC_FDAT


def test_firmup_rewrites_core_when_no_boo_file(tmp_path):
    """Sin darwin_boo.bin (r9=0) el core se reescribe siempre, aunque la versión coincida."""
    capstone = pytest.importorskip("capstone")
    img = NAND / "dev_nflasha1.bin"
    _need(img)
    if not (shutil.which("mcopy") and shutil.which("7z")):
        pytest.skip("faltan mtools/7z")
    subprocess.run(["mcopy", "-s", "-n", "-i", str(img), "::boot", str(tmp_path)], check=True)
    subprocess.run(["7z", "x", "-y", f"-o{tmp_path / 'ird'}", str(tmp_path / "boot/initrd.img")],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elf = (tmp_path / "ird/usr/bin/ud_darwin_firmup.elf").read_bytes()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)

    def dis(addr, n):
        return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(elf[addr - 0x8000:addr - 0x8000 + n], addr)]

    assert dis(0x8F8E, 4) == ["mov.w sb, #0"]  # apertura de darwin_boo.bin fallida: versión del boo = 0
    assert dis(0x9080, 0x14) == ["cmp.w sb, #0", "beq #0x914c", "cmp sb, sl", "bne #0x914c", "cmp r4, #0",
                                 "beq #0x914c", "ldr r3, [r7]", "cmp r4, r3", "bne #0x914c"]  # omite solo si todo coincide
    assert dis(0x914C, 12)[2:] == ["ldr r2, [r7, #4]", "bl #0x8c40"]  # 0x914c = escritura de bloques
