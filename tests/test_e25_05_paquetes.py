"""E25-05 — verificación offline de los paquetes 3.23 (B1a) y 3.24 (recuperación).

Lee los paquetes locales no versionados (`analysis/darwin-patch/fdat/`) y sus manifiestos
(`analysis/e25-05/`); se omiten si los paquetes no están. No toca la cámara.

Informe: docs/capture/e25-05-preparacion-paquetes-323-324.md
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware/extracted/fw321"
PATCH = ROOT / "analysis/darwin-patch"
OUT_EXP = PATCH / "fdat/experimental-323"
OUT_REC = PATCH / "fdat/recuperacion-324"
REC323 = PATCH / "fdat/recuperacion-323"
TIPO0 = PATCH / "darwin_core_tipo0.bin"
B1A = ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin"
MANI = ROOT / "analysis/e25-05"

OFFICIAL_TAR = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
OFFICIAL_UPDATER = "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
OFFICIAL_CORE = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
TIPO0_SHA = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
B1A_SHA = "55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d"
REC323_DAT = "5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf"
EXP_DAT = "4c21353dc742bde86d66de6d3d6bdd8dc18f4c445c436399e768731ccf474542"
EXP_FDAT = "268621fb70948fc58676bb19bcf82e7d73a2634d0085e3032d64833b04fc6e49"
REC_DAT = "e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22"
REC_FDAT = "24ee9b42e9fae29c7a86ec5f17d85d9a5076a8a36698a3766e0b13801126b2c2"


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


def _members(tar_bytes: bytes) -> dict[str, bytes]:
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        return {m.name: tf.extractfile(m).read() for m in tf.getmembers() if m.isfile()}  # type: ignore[union-attr]


@pytest.fixture(scope="module")
def fwtool():
    _need(ROOT / "references/fwtool/fwtool/sony/fdat.py")
    sys.path.insert(0, str(ROOT / "references/fwtool"))
    pytest.importorskip("Cryptodome")
    from fwtool.sony import dat, fdat  # type: ignore[import-not-found]

    return dat, fdat


def _open_dat(fwtool, path: Path):
    dat, fdat = fwtool
    _need(path)
    with path.open("rb") as f:
        container = dat.readDat(f)  # magia, chunks y CRC de DEND
        _, plain = fdat.decryptFdat(container.firmwareData)  # suma y bandera de cada bloque
        buf = io.BytesIO()
        shutil.copyfileobj(plain, buf)
    buf.seek(0)
    parsed = fdat.readFdat(buf)  # magia y CRC-32 de cabecera
    parsed.firmware.seek(0)
    parsed.fs.seek(0)
    return container, parsed, parsed.firmware.read(), parsed.fs.read()


def _ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    """Rangos [inicio, fin) distintos (solo para buffers pequeños)."""
    assert len(a) == len(b)
    out: list[tuple[int, int]] = []
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        if out and i == out[-1][1]:
            out[-1] = (out[-1][0], i + 1)
        else:
            out.append((i, i + 1))
    return out


# ------------------------------------------------------------------------------------------------ manifiestos
def test_manifests_describe_the_pair():
    for name, role, version, order in (
        ("manifest-experimental-323.json", "experimental", "3.23", 1),
        ("manifest-recuperacion-324.json", "recovery", "3.24", 2),
    ):
        doc = json.loads((MANI / name).read_text())
        assert doc["schema"] == "a6000.e25_05.manifest.v1"
        assert (doc["role"], doc["version"], doc["install_order"]) == (role, version, order)
        assert doc["base_commit"] == "f4bb7f50"
        assert doc["outputs"]["header"]["model"] == "0x41030035"
        assert doc["outputs"]["header"]["region"] == 0
        assert doc["outputs"]["header"]["version"] == version
        assert all(c["result"] == "PASS" for c in doc["checks"])
    diffs = json.loads((MANI / "diferencias-binarias.json").read_text())
    assert diffs["b1a_vs_tipo0"]["count"] == 2
    assert diffs["b1a_vs_original"]["count"] == 9


def test_manifests_match_existing_artifacts():
    _need(OUT_EXP / "firmware_packed.dat", OUT_REC / "firmware_packed.dat")
    exp = json.loads((MANI / "manifest-experimental-323.json").read_text())
    rec = json.loads((MANI / "manifest-recuperacion-324.json").read_text())
    assert _sha(OUT_EXP / "firmware_packed.dat") == exp["outputs"]["dat"]["sha256"] == EXP_DAT
    assert _sha(OUT_EXP / "firmware_packed.fdat") == exp["outputs"]["fdat"]["sha256"] == EXP_FDAT
    assert _sha(OUT_REC / "firmware_packed.dat") == rec["outputs"]["dat"]["sha256"] == REC_DAT
    assert _sha(OUT_REC / "firmware_packed.fdat") == rec["outputs"]["fdat"]["sha256"] == REC_FDAT


# ------------------------------------------------------------------------------------------------ contenido
def test_b1a_diff_vs_tipo0_is_only_two_bytes():
    _need(TIPO0, B1A)
    a, b = TIPO0.read_bytes(), B1A.read_bytes()
    assert (len(a), len(b)) == (157276, 157276)
    diff = [(i, a[i], b[i]) for i in range(len(a)) if a[i] != b[i]]
    assert diff == [(0x1BC6A, 0x28, 0x0A), (0x1BC6B, 0x46, 0xE0)]
    assert b[0x20C78 - 0x4200:0x20C78 - 0x4200 + 8] == bytes.fromhex("09e000bf00bf00bf")


def test_experimental_package_is_tipo0_plus_b1a(fwtool):
    _, parsed, tar_bytes, _ = _open_dat(fwtool, OUT_EXP / "firmware_packed.dat")
    assert (parsed.model, parsed.region, parsed.version, parsed.isAccessory) == (0x41030035, 0, "3.23", False)
    files = _members(tar_bytes)
    core = files["0640_darwin/darwin_core.bin"]
    assert hashlib.sha256(core).hexdigest() == B1A_SHA
    assert f"{zlib.crc32(core):08x}" == "cf930ac9"
    assert files["0641_darwin_sum/darwin.sum"].decode().split(",")[:3] == ["0", "cf930ac9", "0002665c"]
    official = _members((FW / "firmware.tar").read_bytes())
    assert sorted(n for n in files if files[n] != official[n]) == [
        "0640_darwin/darwin_core.bin", "0641_darwin_sum/darwin.sum"]


def test_recovery_package_ships_official_darwin(fwtool):
    _, parsed, tar_bytes, _ = _open_dat(fwtool, OUT_REC / "firmware_packed.dat")
    assert (parsed.model, parsed.region, parsed.version, parsed.isAccessory) == (0x41030035, 0, "3.24", False)
    assert hashlib.sha256(tar_bytes).hexdigest() == OFFICIAL_TAR
    files = _members(tar_bytes)
    assert hashlib.sha256(files["0640_darwin/darwin_core.bin"]).hexdigest() == OFFICIAL_CORE
    assert files["0641_darwin_sum/darwin.sum"].decode().split(",")[:3] == ["0", "9ff7148c", "0002665c"]


def test_recovery_reuses_the_verified_323_payload(fwtool):
    _need(REC323 / "firmware_packed.dat")
    assert _sha(REC323 / "firmware_packed.dat") == REC323_DAT
    _, rec323, tar323, fs323 = _open_dat(fwtool, REC323 / "firmware_packed.dat")
    _, rec324, tar324, fs324 = _open_dat(fwtool, OUT_REC / "firmware_packed.dat")
    assert (rec323.version, rec324.version) == ("3.23", "3.24")
    assert tar323 == tar324 and fs323 == fs324
    assert hashlib.sha256(tar324).hexdigest() == OFFICIAL_TAR
    assert hashlib.sha256(fs324).hexdigest() == OFFICIAL_UPDATER


def test_version_order_and_guard_rule():
    order = {v: int(v.split(".")[1], 16) for v in ("3.22", "3.23", "3.24")}
    assert order == {"3.22": 0x22, "3.23": 0x23, "3.24": 0x24}
    assert order["3.22"] < order["3.23"] < order["3.24"]


# ------------------------------------------------------------------------------------------------ diferencias
def test_recovery_fdat_differs_from_323_only_in_header(fwtool):
    _need(REC323 / "firmware_packed.fdat")
    _, fdat = fwtool
    rec, old = (OUT_REC / "firmware_packed.fdat").read_bytes(), (REC323 / "firmware_packed.fdat").read_bytes()
    size = fdat.FdatHeader.size
    assert rec[size:] == old[size:]
    assert [(s, e) for s, e in _ranges(rec[:size], old[:size])] == [(8, 12), (32, 33)]
    assert (rec[32], old[32]) == (0x24, 0x23)


def test_recovery_dat_differs_only_in_first_block_and_dend(fwtool):
    _need(REC323 / "firmware_packed.dat")
    dat, _ = fwtool
    with (OUT_REC / "firmware_packed.dat").open("rb") as f:
        chunks, _ = dat.readChunks(f)
    offset = dict(chunks)[b"FDAT"].offset
    rec, old = (OUT_REC / "firmware_packed.dat").read_bytes(), (REC323 / "firmware_packed.dat").read_bytes()
    assert rec[offset + 512:len(rec) - 4] == old[offset + 512:len(old) - 4]
    assert rec[:offset] == old[:offset]
    assert rec[offset:offset + 512] != old[offset:offset + 512]
    assert rec[-4:] != old[-4:]


# ------------------------------------------------------------------------------------------------ reconstrucción
def test_recovery_324_rebuilds_byte_for_byte(tmp_path, fwtool):
    _need(REC323 / "firmware_packed.dat", OUT_REC / "config-324.yaml")
    dat, _ = fwtool
    with (REC323 / "firmware_packed.dat").open("rb") as f:
        container = dat.readDat(f)
        _, plain = fwtool[1].decryptFdat(container.firmwareData)
        buf = io.BytesIO()
        shutil.copyfileobj(plain, buf)
    buf.seek(0)
    parsed = fwtool[1].readFdat(buf)
    parsed.firmware.seek(0)
    parsed.fs.seek(0)
    (tmp_path / "firmware.tar").write_bytes(parsed.firmware.read())
    (tmp_path / "updater.img").write_bytes(parsed.fs.read())
    subprocess.run([sys.executable, str(ROOT / "references/fwtool/fwtool.py"), "pack",
                    "-c", str(OUT_REC / "config-324.yaml"),
                    "-u", str(tmp_path / "updater.img"),
                    "-f", str(tmp_path / "firmware.tar"), "-o", str(tmp_path)], check=True, capture_output=True)
    assert _sha(tmp_path / "firmware_packed.fdat") == REC_FDAT
    assert _sha(tmp_path / "firmware_packed.dat") == REC_DAT


def test_existing_packages_are_untouched():
    _need(PATCH / "fdat/firmware_packed.dat", REC323 / "firmware_packed.dat")
    assert _sha(PATCH / "fdat/firmware_packed.dat") == \
        "c19a1463a14d2b8038289240aa68d62dfa0de7e07b0db5c513e99565db3305a6"
    assert _sha(REC323 / "firmware_packed.dat") == REC323_DAT
