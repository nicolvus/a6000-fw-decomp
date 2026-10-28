"""E25-06 — auditoría independiente de los paquetes 3.23 (B1a) y 3.24 (recuperación).

Las pruebas negativas mutan copias en memoria o en `tmp_path`; nunca los paquetes de E25-05
(se abren con `mmap` de solo lectura). Si falta un paquete real, las pruebas **fallan**
(no se omiten): una comprobación crítica no ejecutada no cuenta como aprobada.

Informe: docs/capture/e25-06-auditoria-independiente-paquetes.md
"""
from __future__ import annotations

import json
import struct
import sys
import zlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e25_06"))
import audit_packages as A

EXP_DAT = A.EXP_DIR / "firmware_packed.dat"
EXP_FDAT = A.EXP_DIR / "firmware_packed.fdat"
REC_FDAT = A.REC_DIR / "firmware_packed.fdat"


def _require(*paths: Path) -> None:
    missing = [str(p.relative_to(ROOT)) for p in paths if not p.exists()]
    assert not missing, f"faltan paquetes reales: {missing} (prueba crítica no ejecutable = no aprobada)"


@pytest.fixture(scope="module")
def keys():
    return A.load_keys()


@pytest.fixture(scope="module")
def cores():
    _require(A.B1A_CORE, A.TIPO0_CORE, A.OFFICIAL_CORE)
    return A.B1A_CORE.read_bytes(), A.TIPO0_CORE.read_bytes(), A.OFFICIAL_CORE.read_bytes()


@pytest.fixture(scope="module")
def exp_header():
    _require(EXP_FDAT)
    return bytes(A.open_ro(EXP_FDAT)[:A.FDAT_HDR])


def _with_crc(h: bytearray) -> bytes:
    h[8:12] = struct.pack("<I", zlib.crc32(bytes(h[12:A.FDAT_HDR])))
    return bytes(h)


# ------------------------------------------------------------------------------------------------ positiva
def test_full_audit_on_real_packages():
    report = A.run()
    assert all(report["files_present"].values()), report["files_present"]
    failed = [c for c in report["checks"] if c["result"] != "PASS"]
    assert not failed, failed
    assert len(report["checks"]) >= 140


def test_missing_package_is_never_pass(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "EXP_DIR", tmp_path / "experimental-323")
    report = A.run()
    assert any(c["result"] == "MISSING" for c in report["checks"])
    assert not any(c["result"] == "PASS" for c in report["checks"])


def test_manifest_says_pass_but_file_differs(tmp_path):
    _require(A.MANI / "manifest-experimental-323.json")
    manifest = json.loads((A.MANI / "manifest-experimental-323.json").read_text())
    assert all(c["result"] == "PASS" for c in manifest["checks"])
    for name in ("firmware_packed.dat", "firmware_packed.fdat", "config-323.yaml"):
        (tmp_path / name).write_bytes(b"no es el paquete")
    rows = A.manifest_vs_real(manifest, tmp_path)
    assert rows and not any(r["match"] for r in rows)


# ------------------------------------------------------------------------------------------------ Darwin
def test_unauthorized_darwin_byte_is_detected(cores):
    b1a, tipo0, orig = cores
    bad = bytearray(b1a)
    bad[0x8DA8 - A.BASE] ^= 0x01  # Upd main
    c = A.Checks()
    A.audit_darwin(c, bytes(bad), tipo0, orig)
    assert {"darwin.b1a_vs_tipo0_exactly_two", "darwin.b1a_vs_original_is_tipo0_plus_b1a",
            "darwin.critical_regions_untouched"} <= set(c.failed())


def test_removed_tipo0_is_detected_by_bytes_and_emulation(cores):
    b1a, tipo0, orig = cores
    no_tipo0 = bytearray(b1a)
    lo = 0x20C78 - A.BASE
    no_tipo0[lo:lo + 8] = orig[lo:lo + 8]
    c = A.Checks()
    A.audit_darwin(c, bytes(no_tipo0), tipo0, orig)
    assert {"darwin.tipo0_preserved", "darwin.emu.p4d_p4e_filtered"} <= set(c.failed())


def test_original_darwin_instead_of_b1a_is_detected(cores):
    _, tipo0, orig = cores
    c = A.Checks()
    A.audit_darwin(c, orig, tipo0, orig)
    assert {"darwin.b1a_vs_tipo0_exactly_two", "darwin.emu.b1a_returns_zero", "darwin.emu.b1a_no_0x1b080",
            "darwin.branch_target"} <= set(c.failed())


def test_b1a_accidentally_in_recovery_is_detected():
    _require(A.OFFICIAL_TAR, A.B1A_CORE)
    official = A.open_ro(A.OFFICIAL_TAR)
    tref = A.parse_tar(official)
    tar = bytearray(official)
    m = next(x for x in tref["members"] if x["name"] == A.DARWIN_CORE)
    tar[m["data_offset"]:m["data_offset"] + m["size"]] = A.B1A_CORE.read_bytes()
    c = A.Checks()
    A.compare_tars(c, "rec", tar, official, A.parse_tar(tar), tref, set())
    assert "rec.tar.only_authorized_differ" in c.failed()
    assert A.sha256_buf(A.member_bytes(tar, tref, A.DARWIN_CORE)) != A.EXPECT_REC.core_sha


# ------------------------------------------------------------------------------------------------ tar y darwin.sum
def test_non_darwin_tar_member_change_is_detected():
    _require(EXP_FDAT, A.OFFICIAL_TAR)
    fdat = A.open_ro(EXP_FDAT)
    hd = A.parse_fdat_header(bytes(fdat[:A.FDAT_HDR]))
    tar = bytearray(A.slice_of(fdat, (hd["firmware_offset"], hd["firmware_size"])))
    official = A.open_ro(A.OFFICIAL_TAR)
    t = A.parse_tar(tar)
    victim = next(x for x in t["members"] if x["name"].endswith("nflasha3"))
    tar[victim["data_offset"] + 4096] ^= 0xFF
    c = A.Checks()
    A.compare_tars(c, "exp", tar, official, t, A.parse_tar(official), {A.DARWIN_CORE, A.DARWIN_SUM})
    assert "exp.tar.only_authorized_differ" in c.failed()
    assert victim["name"] in c.items[-1]["detail"]["unauthorized"]


@pytest.mark.parametrize("field,value,check", [(1, "cf930ac8", "x.sum.crc"), (2, "0002665d", "x.sum.size"),
                                               (3, "000001ed", "x.sum.mode_matches_tar")])
def test_corrupted_darwin_sum_is_detected(cores, field, value, check):
    b1a = cores[0]
    fields = A.EXP_SUM_LINE.decode().split(",")
    fields[field] = value
    c = A.Checks()
    A.check_sum(c, "x", ",".join(fields).encode(), b1a, A.OFFICIAL_SUM.read_bytes(), 0o644)
    assert check in c.failed() and "x.sum.format" not in c.failed()


def test_darwin_sum_crlf_is_detected(cores):
    c = A.Checks()
    A.check_sum(c, "x", A.EXP_SUM_LINE.replace(b"\n", b"\r\n"), cores[0], A.OFFICIAL_SUM.read_bytes(), 0o644)
    assert "x.sum.format" in c.failed()


# ------------------------------------------------------------------------------------------------ cabecera FDAT
def test_swapped_versions_are_detected(exp_header):
    c = A.Checks()
    A.check_fdat_header(c, "exp", exp_header, A.FDAT_SIZE, A.EXPECT_REC.minor)
    assert c.failed() == ["exp.fdat.version_minor"]
    swapped = bytearray(exp_header)
    swapped[32] = 0x24
    c = A.Checks()
    A.check_fdat_header(c, "exp", _with_crc(swapped), A.FDAT_SIZE, A.EXPECT_EXP.minor)
    assert c.failed() == ["exp.fdat.version_minor"]


@pytest.mark.parametrize("offset,value,check", [(36, 0x36, "exp.fdat.model"), (40, 1, "exp.fdat.region"),
                                                (33, 0x09, "exp.fdat.version_major"), (52, 1, "exp.fdat.offsets"),
                                                (64, ord("P"), "exp.fdat.filesystems")])
def test_altered_fdat_header_is_detected(exp_header, offset, value, check):
    h = bytearray(exp_header)
    h[offset] = value
    c = A.Checks()
    A.check_fdat_header(c, "exp", bytes(h), A.FDAT_SIZE, A.EXPECT_EXP.minor)
    assert "exp.fdat.header_crc" in c.failed()
    c = A.Checks()
    A.check_fdat_header(c, "exp", _with_crc(h), A.FDAT_SIZE, A.EXPECT_EXP.minor)
    assert check in c.failed() and "exp.fdat.header_crc" not in c.failed()


def test_accessory_model_is_rejected(exp_header):
    h = bytearray(exp_header)
    h[36:40] = struct.pack("<I", 0x41A00035)
    c = A.Checks()
    A.check_fdat_header(c, "exp", _with_crc(h), A.FDAT_SIZE, A.EXPECT_EXP.minor)
    assert {"exp.fdat.model", "exp.fdat.not_accessory"} <= set(c.failed())


# ------------------------------------------------------------------------------------------------ contenedor cifrado
def test_altered_encrypted_block_is_detected(keys):
    _require(EXP_DAT)
    dat = bytearray(A.open_ro(EXP_DAT))
    info = A.parse_dat(dat)
    victim = 1000
    dat[info["fdat_offset"] + victim * A.BLOCK + 600] ^= 0x5A
    c = A.Checks()
    A.check_dat(c, "x", A.parse_dat(dat), None)
    assert c.failed() == ["x.dat.dend_crc"]
    # Aun recalculando DEND, la suma de 16 bits del bloque descifrado delata la alteración.
    end = info["chunks"][-1][1]
    dat[end:end + 4] = struct.pack(">I", zlib.crc32(memoryview(dat)[:end - 8]))
    c = A.Checks()
    A.check_dat(c, "x", A.parse_dat(dat), None)
    assert not c.failed()
    dec = A.decrypt_fdat(dat, info["fdat_offset"], info["fdat_size"], keys)
    assert dec.bad_sum == [victim]


def test_dat_not_matching_declared_fdat(keys):
    _require(EXP_DAT, REC_FDAT)
    pkg = A.audit_package("x", A.open_ro(EXP_DAT), A.open_ro(REC_FDAT), A.EXPECT_EXP, keys, None)
    failed = set(pkg.checks.failed())
    assert {"x.dat_matches_fdat", "x.fdat.sha256", "x.fdat.version_minor"} <= failed
    assert "x.blocks.checksums" not in failed
