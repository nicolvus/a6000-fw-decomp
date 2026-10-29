"""E25-27 — construcción integrada, contenedor y emulación (offline)."""
from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for path in ("scripts", "scripts/e25_18", "scripts/e25_16", "scripts/e25_17"):
    sys.path.insert(0, str(ROOT / path))

from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD
from e25_26 import patch_c3b as PC
from e25_27 import build, emu, fatimg, sums, tarball, tpzl

FW_TAR = ROOT / "firmware/extracted/fw321/firmware.tar"
AV_CAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
ARTIFACTS = ROOT / "analysis/e25-27/artifacts"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# --------------------------------------------------------------------- TPZL


def test_tpzl_literal_roundtrip():
    data = bytes((i * 37 + 11) & 0xFF for i in range(65536))
    encoded = tpzl.encode_literal(data)
    assert tpzl.decode_block(encoded, len(data)) == data


def test_tpzl_bloque_corto_y_vacio():
    for size in (1, 7, 8, 9, 4096):
        data = bytes(range(256)) * (size // 256) + bytes(range(size % 256))
        assert tpzl.decode_block(tpzl.encode_literal(data), size) == data


def test_tpzl_tipo_sin_comprimir():
    # type 0x0f: un byte sin usar + longitud LE16 + datos.
    raw = bytes(range(64))
    block = b"\x0f\x00" + struct.pack("<H", len(raw)) + raw
    assert tpzl.decode_block(block, len(raw)) == raw


def test_tpzl_rechaza_magia():
    with pytest.raises(tpzl.TpzlError):
        tpzl.TpzlImage.parse(b"NOPE" + b"\0" * 32)


# --------------------------------------------------------------------- FAT12


def _fat12_image(name: str, payload: bytes) -> bytes:
    bps, spc, reserved, nfats, root_entries, total = 512, 1, 1, 1, 16, 64
    fat_size = 1
    root_off = (reserved + nfats * fat_size) * bps
    data_off = root_off + root_entries * 32
    img = bytearray(total * bps)
    img[0:3] = b"\xeb\x3c\x90"
    struct.pack_into("<H", img, 0x0B, bps)
    img[0x0D] = spc
    struct.pack_into("<H", img, 0x0E, reserved)
    img[0x10] = nfats
    struct.pack_into("<H", img, 0x11, root_entries)
    struct.pack_into("<H", img, 0x13, total)
    struct.pack_into("<H", img, 0x16, fat_size)
    img[510:512] = b"\x55\xaa"
    clusters = (len(payload) + bps - 1) // bps
    # FAT12: clúster 2 -> 3 -> ... -> EOC
    fat = bytearray(512)
    for i in range(clusters):
        cluster = 2 + i
        nxt = cluster + 1 if i + 1 < clusters else 0xFFF
        offset = (cluster * 3) // 2
        word = struct.unpack_from("<H", fat, offset)[0]
        if cluster & 1:
            word = (word & 0x000F) | (nxt << 4)
        else:
            word = (word & 0xF000) | nxt
        struct.pack_into("<H", fat, offset, word)
    img[reserved * bps:reserved * bps + 512] = fat
    entry = bytearray(32)
    base, ext = name.split(".")
    entry[:8] = base.encode().ljust(8)
    entry[8:11] = ext.encode().ljust(3)
    entry[11] = 0x20
    struct.pack_into("<H", entry, 26, 2)
    struct.pack_into("<I", entry, 28, len(payload))
    img[root_off:root_off + 32] = entry
    img[data_off:data_off + len(payload)] = payload
    return bytes(img)


def test_fat12_lee_y_parchea():
    original = bytes((i * 7) & 0xFF for i in range(700))
    img = _fat12_image("TEST.BIN", original)
    fat = fatimg.Fat16.parse(img)
    assert fat.fat_type == 12
    assert fat.read("TEST.BIN") == original
    patched = bytes((b ^ 0x5A) for b in original)
    out, info = fat.patch("TEST.BIN", patched)
    assert info["changed_bytes"] == len(original)
    assert fatimg.Fat16.parse(out).read("TEST.BIN") == patched
    assert len(out) == len(img)


def test_fat_rechaza_tamano_distinto():
    img = _fat12_image("TEST.BIN", b"x" * 600)
    fat = fatimg.Fat16.parse(img)
    with pytest.raises(fatimg.FatError):
        fat.patch("TEST.BIN", b"x" * 700)


# --------------------------------------------------------------------- tar


def _tiny_tar() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, data in (("a.bin", b"A" * 100), ("b.bin", b"B" * 50)):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = 1_548_295_903
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_tar_reemplaza_y_conserva():
    original = _tiny_tar()
    new = b"C" * 4096
    out, info = tarball.rebuild(original, {"a.bin": new})
    entries, _ = tarball.parse(out)
    data = {e.name: e.data for e in entries}
    assert data["a.bin"] == new and data["b.bin"] == b"B" * 50
    assert info[0]["size_old"] == 100 and info[0]["size_new"] == 4096


def test_tar_rechaza_miembro_ausente():
    with pytest.raises(tarball.TarError):
        tarball.rebuild(_tiny_tar(), {"nope.bin": b"x"})


# --------------------------------------------------------------------- sums


def test_sums_actualiza_crc_y_tamano():
    text = "0,00000000,00000000,000001a4,00000000,000003e8,root,root,-1,-1,dev/nflasha3,\n"
    data = b"abc"
    out, info = sums.update(text, "dev/nflasha3", data)
    assert info["crc32_after"] == f"{sums.crc32(data):08x}"
    assert info["size_after"] == "00000003"
    assert sums.verify(out, "dev/nflasha3", data)
    assert len(out) == len(text)


# --------------------------------------------------------------------- construcción real


def _require_firmware() -> None:
    if not FW_TAR.is_file() or not AV_CAM.is_file():
        pytest.skip("falta el firmware original no versionado")


def test_apply_patches_y_reversion():
    _require_firmware()
    originals = build.load_originals()
    built = build.apply_patches(originals.avcam, originals.darwin)
    assert _sha(built["bionz"]) != PB.SHA256 and _sha(built["darwin"]) != PD.SHA256
    assert PB.restore_bytes(built["selector"]) == originals.avcam
    assert PC.restore_bytes(built["bionz"]) == built["selector"]
    assert PD.restore_bytes(built["darwin"]) == originals.darwin
    assert not ({d["address"] for d in built["diff_selector"]}
                & {d["address"] for d in built["diff_c3b"]})


def test_rechaza_entrada_ya_parcheada():
    _require_firmware()
    originals = build.load_originals()
    patched = PB.apply_bytes(originals.avcam)[0]
    with pytest.raises(build.BuildError):
        build.apply_patches(patched, originals.darwin)


def test_build_completo_y_determinista(tmp_path: Path):
    _require_firmware()
    first = build.build(tmp_path / "a")
    second = build.build(tmp_path / "b")
    assert first["outputs"] == second["outputs"]
    assert first["status"] == build.STATUS and first["installable"] is False
    assert first["diff_count"] > 0
    assert first["cave_overlap"]["overlap"] is False
    assert first["partition"]["changed_blocks"] == [0, 48, 57]

    originals = build.load_originals()
    out = tmp_path / "a"
    tar_bytes = (out / "firmware.integrated.tar").read_bytes()
    entries, _ = tarball.parse(tar_bytes)
    got = {e.name: e.data for e in entries}
    old = {e.name: e.data for e in tarball.parse(originals.tar)[0]}
    changed = sorted(name for name in got if got[name] != old[name])
    assert changed == [build.DARWIN_CORE, build.DARWIN_SUM, build.NFLASHA3, build.PART_SUM]
    assert got[build.DARWIN_CORE] == (out / "darwin_core.integrated.bin").read_bytes()
    assert got[build.NFLASHA3] == (out / "nflasha3.integrated.bin").read_bytes()

    part = tpzl.TpzlImage.parse(got[build.NFLASHA3])
    fat = fatimg.Fat16.parse(part.decompressed())
    assert fat.read(build.AVCAM_NAME) == (out / "av-cam.integrated.bin").read_bytes()
    assert sums.verify(got[build.PART_SUM].decode(), build.PART_ENTRY, got[build.NFLASHA3])
    # La partición nflasha3 tiene 30 MB (partinf.conf): el crecimiento cabe.
    assert len(got[build.NFLASHA3]) < 0x01E00000
    assert len(part.decompressed()) == 24_182_784


def test_restore_exacto(tmp_path: Path):
    _require_firmware()
    build.build(tmp_path)
    payload = build.restore(tmp_path)
    assert payload["verified"] is True
    assert payload["bionz"]["restored_sha256"] == PB.SHA256
    assert payload["darwin"]["restored_sha256"] == PD.SHA256
    assert (tmp_path / "av-cam.restored.bin").read_bytes() == build.load_originals().avcam


# --------------------------------------------------------------------- emulación integrada


def test_emulacion_integrada():
    _require_firmware()
    pytest.importorskip("unicorn")
    pytest.importorskip("capstone")
    originals = build.load_originals()
    built = build.apply_patches(originals.avcam, originals.darwin)
    result = emu.matrix(built["bionz"], built["darwin"], originals.avcam)
    assert result["all_ok"] is True
    assert result["efcs_identical"] is True
    assert result["electronic_normalized"] is True
    assert result["alternation_ok"] is True
    assert result["speeds_ok"] is True
    assert result["invalid_field"] == "InvalidSelection"
    assert result["speeds"]["1/8000"]["electronic"]["shd"] == 4211
    assert result["speeds"]["1/4000"]["electronic"]["shd"] == 4203
    assert result["speeds"]["1/30"]["electronic"]["shd"] == 2025
    assert result["errors"]["long_route"]["svd_SetExposure"] == 2


# --------------------------------------------------------------------- contenedor


def test_contenedor_si_existe():
    container = ARTIFACTS / "container.json"
    if not container.is_file():
        pytest.skip("no hay contenedor construido")
    data = json.loads(container.read_text())
    assert data["phase"] == "E25-27" and data["installable"] is False
    assert data["version"] == build.VERSION
    assert data["header"]["model"] == f"0x{build.MODEL:08x}"
    assert data["header"]["version"] == build.VERSION
    assert data["roundtrip"]["part_sum_verified"] is True
    for key in ("fdat", "dat"):
        path = Path(data[key]["path"])
        if not path.is_file():
            pytest.skip(f"falta {path}")
        assert _sha(path.read_bytes()) == data[key]["sha256"]


def test_evidencia_versionada():
    manifest_path = ROOT / "analysis/e25-27/manifest.json"
    evidence_path = ROOT / "analysis/e25-27/evidence.json"
    if not manifest_path.is_file() or not evidence_path.is_file():
        pytest.skip("falta la evidencia versionada")
    manifest = json.loads(manifest_path.read_text())
    evidence = json.loads(evidence_path.read_text())
    assert manifest["status"] == build.STATUS and manifest["installable"] is False
    assert manifest["diff_count"] == len(manifest["diff"])
    allowed = PB.allowed_addresses() | PD.allowed_addresses() | PC.allowed_addresses()
    assert {item["address"] for item in manifest["diff"]} <= allowed
    assert manifest["cave_overlap"]["overlap"] is False
    assert evidence["emulation"]["all_ok"] is True
    assert evidence["reversal"]["verified"] is True
    assert evidence["partition"]["changed_blocks"] == [0, 48, 57]
    assert evidence["independent_audit"]["ok"] is True
    assert evidence["status"] == build.STATUS
    assert manifest["outputs"]["av-cam.bin"]["sha256"] == evidence["outputs"]["av-cam.bin"]["sha256"]
