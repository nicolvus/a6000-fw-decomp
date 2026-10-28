#!/usr/bin/env python3
"""E25-05 — prepara offline los paquetes 3.23 (experimental) y 3.24 (recuperación).

No conecta la cámara, no ejecuta firmware, no escribe RAM/NVRAM/NAND y no flashea.
Construye cada paquete en su propio directorio, reutiliza el contenido ya verificado
de la recuperación 3.23 como base de la 3.24 y comprueba hashes, CRC, integridad,
modelo, región, versión y diferencias binarias contra los paquetes existentes.

Los `.fdat`/`.dat` van a `analysis/darwin-patch/fdat/` (ignorado por git: firmware de
Sony). Los manifiestos van a `analysis/e25-05/` (versionados). Informe:
`docs/capture/e25-05-preparacion-paquetes-323-324.md`.

Uso:
    .venv/bin/python scripts/e25_05/build_packages.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zlib
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FW = ROOT / "firmware/extracted/fw321"
PATCH = ROOT / "analysis/darwin-patch"
FDAT_ROOT = PATCH / "fdat"
OUT_EXP = FDAT_ROOT / "experimental-323"
OUT_REC = FDAT_ROOT / "recuperacion-324"
MANI_DIR = ROOT / "analysis/e25-05"
FWTOOL = ROOT / "references/fwtool/fwtool.py"

BASE_COMMIT = "f4bb7f50"

# Entradas fijadas (no se reescriben en esta sesión) -------------------------------------------
OFFICIAL_TAR_SHA = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
OFFICIAL_UPDATER_SHA = "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
OFFICIAL_CORE_SHA = "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
OFFICIAL_CORE_CRC32 = "9ff7148c"
TIPO0_CORE_SHA = "ca41b46c43d4324a20414692fa081c4cfbffa96dce58bd61c0af2c7060fa52dc"
B1A_CORE_SHA = "55a366a5fc95f01ccb044ae352db90f0122ee779cab69063b6b99da8b3dcea1d"

REC323_DAT_SHA = "5f10890110bd9bf760a33288e5facfcee4b41a79fe35192c3f5ce83196c0ceaf"
REC323_FDAT_SHA = "cfb65c8aad8ac8a3ccb1c4c758d485feee1ebf2e83e503d9c62d59fb96b01ce4"
INSTALLED322_DAT_SHA = "c19a1463a14d2b8038289240aa68d62dfa0de7e07b0db5c513e99565db3305a6"
INSTALLED322_FDAT_SHA = "ddc2d5db41cfd049be6b64d702f544ecb6b8e92f6150782097ddb95dccb33295"

MODEL = 0x41030035
REGION = 0
SIZE_CORE = 157276
DARWIN_CORE = "0640_darwin/darwin_core.bin"
DARWIN_SUM = "0641_darwin_sum/darwin.sum"
DARWIN_FILES = (DARWIN_CORE, DARWIN_SUM)
DESCRIPTORS_UPDATER = [(0x54C, 0x3E2)]
TIPO0_BYTES = bytes.fromhex("09e000bf00bf00bf")
TIPO0_ADDR = 0x20C78
BASE = 0x4200


# ------------------------------------------------------------------------------------------- utilidades
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda f=f: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crc32_hex(data: bytes) -> str:
    return f"{zlib.crc32(data):08x}"


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def check(checks: list[dict], cid: str, ok: bool, detail: str) -> None:
    checks.append({"id": cid, "result": "PASS" if ok else "FAIL", "detail": detail})
    if not ok:
        raise SystemExit(f"FALLO {cid}: {detail}")


def diff_ranges(a: bytes, b: bytes, chunk: int = 1 << 20) -> list[list[int]]:
    """Rangos [inicio, fin) de bytes distintos entre dos buffers del mismo tamaño."""
    if len(a) != len(b):
        raise ValueError(f"tamaños distintos: {len(a)} != {len(b)}")
    out: list[list[int]] = []
    start: int | None = None
    for off in range(0, len(a), chunk):
        ca, cb = a[off:off + chunk], b[off:off + chunk]
        if ca == cb:
            if start is not None:
                out.append([start, off])
                start = None
            continue
        for i in range(len(ca)):
            if ca[i] != cb[i]:
                if start is None:
                    start = off + i
            elif start is not None:
                out.append([start, off + i])
                start = None
    if start is not None:
        out.append([start, len(a)])
    return out


def diff_positions(a: bytes, b: bytes) -> list[dict]:
    """Posiciones distintas con sus valores (para ficheros pequeños)."""
    if len(a) != len(b):
        raise ValueError(f"tamaños distintos: {len(a)} != {len(b)}")
    return [
        {"file_offset": i, "before": f"{x:02x}", "after": f"{y:02x}"}
        for i, (x, y) in enumerate(zip(a, b)) if x != y
    ]


# ------------------------------------------------------------------------------------------- tar
def tar_member_offsets(path: Path) -> dict[str, tuple[int, int]]:
    with tarfile.open(path) as tf:
        return {m.name: (m.offset_data, m.size) for m in tf.getmembers() if m.isfile()}


def tar_member_hashes(path: Path) -> dict[str, tuple[str, int]]:
    out: dict[str, tuple[str, int]] = {}
    with tarfile.open(path) as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            h = hashlib.sha256()
            f = tf.extractfile(m)
            assert f is not None
            for chunk in iter(lambda f=f: f.read(1 << 20), b""):
                h.update(chunk)
            out[m.name] = (h.hexdigest(), m.size)
    return out


def tar_member_bytes(path: Path, wanted: tuple[str, ...]) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    with tarfile.open(path) as tf:
        for m in tf.getmembers():
            if m.name in wanted:
                f = tf.extractfile(m)
                assert f is not None
                out[m.name] = f.read()
    return out


def patch_tar_in_place(tar_bytes: bytes, tar_path: Path, replacements: dict[str, bytes]) -> bytes:
    """Sustituye ficheros por contenido de igual tamaño; cabeceras y orden intactos."""
    offsets = tar_member_offsets(tar_path)
    patched = bytearray(tar_bytes)
    done: set[str] = set()
    for name, data in replacements.items():
        off, size = offsets[name]
        if len(data) != size:
            raise ValueError(f"{name}: {len(data)} != {size}")
        patched[off:off + size] = data
        done.add(name)
    if done != set(replacements):
        raise ValueError(f"miembros no encontrados: {set(replacements) - done}")
    assert len(patched) == len(tar_bytes)
    return bytes(patched)


# ------------------------------------------------------------------------------------------- darwin.sum
def build_darwin_sum(core: bytes, template: bytes) -> bytes:
    """Reescribe CRC-32 y tamaño conservando el resto de campos del sum oficial."""
    line = template.decode("ascii").rstrip("\n")
    fields = line.split(",")
    if len(fields) < 11 or fields[0] != "0" or fields[10] != "darwin_core.bin":
        raise ValueError(f"formato de darwin.sum inesperado: {line!r}")
    fields[2] = f"{len(core):08x}"
    fields[1] = crc32_hex(core)
    out = (",".join(fields) + "\n").encode("ascii")
    if len(out) != len(template):
        raise ValueError("darwin.sum cambiaría de tamaño")
    return out


# ------------------------------------------------------------------------------------------- configuración
def config_for(version: str, template_text: str) -> str:
    if not re.fullmatch(r"3\.(2[3-9])", version):
        raise ValueError(f"versión fuera del rango previsto: {version}")
    text = template_text.replace("version: '3.21'", f"version: '{version}'")
    if text == template_text:
        raise ValueError("no se encontró la versión 3.21 en la plantilla")
    import yaml

    parsed = yaml.safe_load(text)
    if parsed["fdat"] != {"isAccessory": False, "model": MODEL, "region": REGION, "version": version}:
        raise ValueError(f"config inesperada: {parsed['fdat']}")
    if parsed["dat"]["crypterName"] != "CXD90014" or parsed["dat"]["isLens"]:
        raise ValueError("config: crypter/isLens inesperados")
    if parsed["dat"]["updaterUsbDescriptors"] != [[0x54C, 0x3E2]]:
        raise ValueError("config: descriptores USB del actualizador inesperados")
    return text


# ------------------------------------------------------------------------------------------- fwtool
def run_fwtool(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(FWTOOL), *args],
        check=True, capture_output=True, text=True,
    )


def pack(config: Path, tar_file: Path, updater: Path, outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    run_fwtool(["pack", "-c", str(config), "-u", str(updater), "-f", str(tar_file), "-o", str(outdir)])


def unpack(dat_file: Path, outdir: Path) -> None:
    """Descifra y valida el paquete con fwtool (DEND, cabecera, suma por bloque)."""
    outdir.mkdir(parents=True, exist_ok=True)
    run_fwtool(["unpack", "-f", str(dat_file), "-o", str(outdir)])


def _fwtool_module():
    sys.path.insert(0, str(ROOT / "references/fwtool"))
    from fwtool.sony import dat as datmod
    from fwtool.sony import fdat as fdatmod

    return datmod, fdatmod


def header_of(fdat_file: Path) -> dict:
    _, fdatmod = _fwtool_module()
    with fdat_file.open("rb") as f:
        h = fdatmod.FdatHeader.unpack(f)
    return {
        "magic": h.magic.decode("ascii"),
        "fdat_version": h.version.decode("ascii"),
        "checksum_crc32": f"0x{h.checksum:08x}",
        "mode": h.modeType.decode("ascii"),
        "luw": h.luwFlag.decode("ascii"),
        "version_major": h.versionMajor,
        "version_minor": f"0x{h.versionMinor:02x}",
        "version": f"{h.versionMajor:x}.{h.versionMinor:02x}",
        "model": f"0x{h.model:08x}",
        "region": h.region,
        "is_accessory": bool(h.model & 0xFF0000 == 0xA00000),
        "firmware_offset": h.firmwareOffset,
        "firmware_size": h.firmwareSize,
        "num_filesystems": h.numFileSystems,
        "header_size": fdatmod.FdatHeader.size,
    }


def dat_info(dat_file: Path) -> dict:
    datmod, _ = _fwtool_module()
    with dat_file.open("rb") as f:
        chunks, _ = datmod.readChunks(f)
        f.seek(0)
        contents = datmod.readDat(f)  # valida magia, chunks y CRC de DEND
    fdat_part = dict(chunks)[b"FDAT"]
    return {
        "magic": "895546550d0a1a0a",
        "normal_usb_descriptors": [[v, p] for v, p in contents.normalUsbDescriptors],
        "updater_usb_descriptors": [[v, p] for v, p in contents.updaterUsbDescriptors],
        "is_lens": contents.isLens,
        "payload_offset": fdat_part.offset,
        "payload_size": fdat_part.size,
    }


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ------------------------------------------------------------------------------------------- verificación
def verify_package(
    checks: list[dict],
    *,
    prefix: str,
    package_dir: Path,
    version: str,
    expected_tar_sha: str,
    expected_updater_sha: str,
    core_sha: str,
    core_crc32: str,
    sum_expected: bytes | None,
) -> dict:
    """Descifra el paquete y comprueba cabecera, payload y contenido Darwin."""
    fdat_file = package_dir / "firmware_packed.fdat"
    dat_file = package_dir / "firmware_packed.dat"
    check(checks, f"{prefix}.files_exist", fdat_file.exists() and dat_file.exists(),
          "firmware_packed.fdat y firmware_packed.dat presentes")
    check(checks, f"{prefix}.fdat_magic", read_bytes(fdat_file)[:8] == b"UDTRFIRM", "cabecera FDAT 'UDTRFIRM'")
    check(checks, f"{prefix}.dat_magic", read_bytes(dat_file)[:8] == bytes.fromhex("895546550d0a1a0a"),
          "contenedor .dat con magia oficial")

    with tempfile.TemporaryDirectory(prefix="e25-05-verify-") as tmp:
        tmpdir = Path(tmp)
        unpack(dat_file, tmpdir)
        tar_file, updater_file = tmpdir / "firmware.tar", tmpdir / "updater.img"
        decrypted = tmpdir / "firmware.fdat"
        check(checks, f"{prefix}.unpack_ok", all(p.exists() for p in (tar_file, updater_file, decrypted)),
              "fwtool unpack descifra y valida DEND, CRC de cabecera y suma de cada bloque")
        check(checks, f"{prefix}.tar_sha", sha256(tar_file) == expected_tar_sha,
              f"firmware.tar = {sha256(tar_file)}")
        check(checks, f"{prefix}.updater_sha", sha256(updater_file) == expected_updater_sha,
              f"updater.img = {sha256(updater_file)}")
        check(checks, f"{prefix}.fdat_roundtrip", sha256(decrypted) == sha256(fdat_file),
              "el .fdat descifrado del .dat coincide con el .fdat empaquetado")
        config_text = (tmpdir / "config.yaml").read_text()
        check(checks, f"{prefix}.unpacked_config_version",
              f"version: '{version}'" in config_text and "model: 0x41030035" in config_text,
              f"config descifrada: versión {version}, modelo 0x41030035")
        members = tar_member_bytes(tar_file, DARWIN_FILES)
        check(checks, f"{prefix}.tar_core", sha256_bytes(members[DARWIN_CORE]) == core_sha,
              f"darwin_core.bin = {sha256_bytes(members[DARWIN_CORE])}")
        check(checks, f"{prefix}.tar_core_crc", crc32_hex(members[DARWIN_CORE]) == core_crc32,
              f"CRC-32 del core = {core_crc32}")
        if sum_expected is not None:
            check(checks, f"{prefix}.tar_sum", members[DARWIN_SUM] == sum_expected,
                  "darwin.sum coincide con el recalculado")
        names = tar_member_hashes(tar_file)
        check(checks, f"{prefix}.no_darwin_boo",
              not [n for n in names if "darwin_boo" in n or "loader" in n.lower()],
              "sin darwin_boo.bin ni loader en el paquete")

    hdr = header_of(fdat_file)
    check(checks, f"{prefix}.header_version", hdr["version"] == version, f"versión de cabecera {hdr['version']}")
    check(checks, f"{prefix}.header_model", hdr["model"] == f"0x{MODEL:08x}", f"modelo {hdr['model']}")
    check(checks, f"{prefix}.header_region", hdr["region"] == REGION, f"región {hdr['region']}")
    check(checks, f"{prefix}.header_accessory", hdr["is_accessory"] is False, "isAccessory = False")
    check(checks, f"{prefix}.header_mode", hdr["mode"] == "U" and hdr["luw"] == "N", "modo U / LUW N")
    check(checks, f"{prefix}.header_filesystems_count", hdr["num_filesystems"] == 2, "2 sistemas de ficheros")

    dinfo = dat_info(dat_file)
    check(checks, f"{prefix}.dat_descriptors",
          dinfo["updater_usb_descriptors"] == [list(d) for d in DESCRIPTORS_UPDATER],
          f"descriptores del actualizador {dinfo['updater_usb_descriptors']}")
    check(checks, f"{prefix}.dat_is_lens", dinfo["is_lens"] is False, "isLens = False")

    return {
        "header": hdr,
        "container": dinfo,
        "fdat": {"path": rel(fdat_file), "sha256": sha256(fdat_file), "size": fdat_file.stat().st_size},
        "dat": {"path": rel(dat_file), "sha256": sha256(dat_file), "size": dat_file.stat().st_size},
    }


# ------------------------------------------------------------------------------------------- construcción
def snapshot(paths: list[Path]) -> dict[str, str]:
    return {rel(p): sha256(p) for p in paths if p.exists()}


def build_experimental(checks: list[dict]) -> dict:
    official_tar = FW / "firmware.tar"
    official_updater = FW / "updater.img"
    official_sum = FW / "firmware.tar_unpacked/0641_darwin_sum/darwin.sum"
    tipo0 = PATCH / "darwin_core_tipo0.bin"
    b1a = ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin"
    template_cfg = (FW / "config.yaml").read_text()

    check(checks, "exp.input.tar", sha256(official_tar) == OFFICIAL_TAR_SHA, "firmware.tar oficial 3.21")
    check(checks, "exp.input.updater", sha256(official_updater) == OFFICIAL_UPDATER_SHA, "updater.img oficial")
    check(checks, "exp.input.tipo0", sha256(tipo0) == TIPO0_CORE_SHA, "Darwin tipo 0 instalado (3.22)")
    check(checks, "exp.input.b1a", sha256(b1a) == B1A_CORE_SHA, "candidato B1a")
    check(checks, "exp.input.official_sum_crc",
          crc32_hex(read_bytes(FW / "firmware.tar_unpacked/0640_darwin/darwin_core.bin")) == OFFICIAL_CORE_CRC32,
          "CRC-32 del core oficial coincide con darwin.sum")

    core_b1a = read_bytes(b1a)
    core_tipo0 = read_bytes(tipo0)
    check(checks, "exp.b1a_size", len(core_b1a) == SIZE_CORE, f"{len(core_b1a)} B")
    diff = diff_positions(core_tipo0, core_b1a)
    check(checks, "exp.b1a_diff_vs_tipo0_two_bytes",
          diff == [{"file_offset": 0x1BC6A, "before": "28", "after": "0a"},
                   {"file_offset": 0x1BC6B, "before": "46", "after": "e0"}],
          f"B1a vs tipo 0: {diff}")
    check(checks, "exp.tipo0_patch_preserved",
          core_b1a[TIPO0_ADDR - BASE:TIPO0_ADDR - BASE + 8] == TIPO0_BYTES,
          "los 8 B del filtro tipo 0 (0x20c78) siguen intactos en B1a")

    sum_b1a = build_darwin_sum(core_b1a, read_bytes(official_sum))
    check(checks, "exp.sum_crc", crc32_hex(core_b1a) in sum_b1a.decode(),
          f"darwin.sum lleva el CRC-32 {crc32_hex(core_b1a)}")
    check(checks, "exp.sum_size", f"{len(core_b1a):08x}" in sum_b1a.decode(), "darwin.sum lleva el tamaño 0002665c")

    replacements = {DARWIN_CORE: core_b1a, DARWIN_SUM: sum_b1a}
    tar_bytes = patch_tar_in_place(read_bytes(official_tar), official_tar, replacements)
    check(checks, "exp.tar_size", len(tar_bytes) == official_tar.stat().st_size,
          "firmware.tar conserva tamaño y cabeceras")

    cfg_text = config_for("3.23", template_cfg)
    work = Path(tempfile.mkdtemp(prefix="e25-05-exp-"))
    try:
        tar_path = work / "firmware_b1a.tar"
        cfg_path = work / "config-323.yaml"
        tar_path.write_bytes(tar_bytes)
        cfg_path.write_text(cfg_text)
        pack(cfg_path, tar_path, official_updater, work / "out")

        official_hashes = tar_member_hashes(official_tar)
        patched_hashes = tar_member_hashes(tar_path)
        changed = sorted(n for n, (h, _) in patched_hashes.items() if official_hashes[n][0] != h)
        check(checks, "exp.tar_changed_only_darwin", changed == sorted(DARWIN_FILES),
              f"miembros distintos del tar oficial: {changed}")

        OUT_EXP.mkdir(parents=True, exist_ok=True)
        for name in ("firmware_packed.fdat", "firmware_packed.dat"):
            shutil.copy2(work / "out" / name, OUT_EXP / name)
        (OUT_EXP / "config-323.yaml").write_text(cfg_text)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    result = verify_package(
        checks, prefix="exp", package_dir=OUT_EXP, version="3.23",
        expected_tar_sha=sha256_bytes(tar_bytes), expected_updater_sha=OFFICIAL_UPDATER_SHA,
        core_sha=B1A_CORE_SHA, core_crc32=crc32_hex(core_b1a), sum_expected=sum_b1a,
    )
    result.update({
        "config": {"path": rel(OUT_EXP / "config-323.yaml"), "sha256": sha256(OUT_EXP / "config-323.yaml")},
        "payload": {"firmware_tar_sha256": sha256_bytes(tar_bytes), "updater_img_sha256": OFFICIAL_UPDATER_SHA},
        "darwin": {
            "core_path": rel(b1a),
            "core_sha256": B1A_CORE_SHA,
            "core_crc32": crc32_hex(core_b1a),
            "core_size": len(core_b1a),
            "sum_sha256": sha256_bytes(sum_b1a),
            "sum_line": sum_b1a.decode().strip(),
            "diff_vs_tipo0_count": len(diff),
            "diff_vs_tipo0": diff,
            "tipo0_patch_preserved": True,
        },
        "tar_members_changed_vs_official": changed,
    })
    return result


def build_recovery(checks: list[dict]) -> dict:
    rec323_dat = FDAT_ROOT / "recuperacion-323/firmware_packed.dat"
    rec323_fdat = FDAT_ROOT / "recuperacion-323/firmware_packed.fdat"
    template_cfg = (FW / "config.yaml").read_text()

    check(checks, "rec.input.323_dat", sha256(rec323_dat) == REC323_DAT_SHA, "paquete de recuperación 3.23 (.dat)")
    check(checks, "rec.input.323_fdat", sha256(rec323_fdat) == REC323_FDAT_SHA, "paquete de recuperación 3.23 (.fdat)")

    work = Path(tempfile.mkdtemp(prefix="e25-05-rec-"))
    try:
        base = work / "base-323"
        unpack(rec323_dat, base)
        base_tar, base_updater = base / "firmware.tar", base / "updater.img"
        check(checks, "rec.reuse.323_tar_official", sha256(base_tar) == OFFICIAL_TAR_SHA,
              "el tar del 3.23 es el oficial (reutilizado como base)")
        check(checks, "rec.reuse.323_updater_official", sha256(base_updater) == OFFICIAL_UPDATER_SHA,
              "el updater.img del 3.23 es el oficial (reutilizado como base)")
        check(checks, "rec.reuse.323_version", "version: '3.23'" in (base / "config.yaml").read_text(),
              "el paquete base declara 3.23")
        base_core = tar_member_bytes(base_tar, DARWIN_FILES)[DARWIN_CORE]
        check(checks, "rec.reuse.323_core_official",
              sha256_bytes(base_core) == OFFICIAL_CORE_SHA and crc32_hex(base_core) == OFFICIAL_CORE_CRC32,
              "el core del 3.23 es el original (Darwin conocido y funcional)")

        cfg_text = config_for("3.24", template_cfg)
        cfg_path = work / "config-324.yaml"
        cfg_path.write_text(cfg_text)
        pack(cfg_path, base_tar, base_updater, work / "out")

        OUT_REC.mkdir(parents=True, exist_ok=True)
        for name in ("firmware_packed.fdat", "firmware_packed.dat"):
            shutil.copy2(work / "out" / name, OUT_REC / name)
        (OUT_REC / "config-324.yaml").write_text(cfg_text)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    result = verify_package(
        checks, prefix="rec", package_dir=OUT_REC, version="3.24",
        expected_tar_sha=OFFICIAL_TAR_SHA, expected_updater_sha=OFFICIAL_UPDATER_SHA,
        core_sha=OFFICIAL_CORE_SHA, core_crc32=OFFICIAL_CORE_CRC32,
        sum_expected=read_bytes(FW / "firmware.tar_unpacked/0641_darwin_sum/darwin.sum"),
    )
    result.update({
        "config": {"path": rel(OUT_REC / "config-324.yaml"), "sha256": sha256(OUT_REC / "config-324.yaml")},
        "payload": {"firmware_tar_sha256": OFFICIAL_TAR_SHA, "updater_img_sha256": OFFICIAL_UPDATER_SHA},
        "reused_from": {
            "package": rel(FDAT_ROOT / "recuperacion-323"),
            "dat_sha256": REC323_DAT_SHA,
            "fdat_sha256": REC323_FDAT_SHA,
            "firmware_tar_sha256": OFFICIAL_TAR_SHA,
            "updater_img_sha256": OFFICIAL_UPDATER_SHA,
            "darwin_core_sha256": OFFICIAL_CORE_SHA,
        },
    })
    return result


# ------------------------------------------------------------------------------------------- manifiestos
def write_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def package_checksums(package_dir: Path) -> None:
    files = sorted(p for p in package_dir.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    lines = [f"{sha256(p)}  {p.name}" for p in files]
    (package_dir / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    if not (FW / "firmware.tar").exists():
        raise SystemExit("faltan los archivos oficiales en firmware/extracted/fw321 (no versionados)")

    checks: list[dict] = []
    watched = [
        FDAT_ROOT / "firmware_packed.dat", FDAT_ROOT / "firmware_packed.fdat",
        FDAT_ROOT / "firmware_tipo0.tar",
        FDAT_ROOT / "recuperacion-323/firmware_packed.dat",
        FDAT_ROOT / "recuperacion-323/firmware_packed.fdat",
        FDAT_ROOT / "recuperacion-323/config-323.yaml",
        PATCH / "darwin_core_tipo0.bin",
        ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin",
    ]
    before = snapshot(watched)
    check(checks, "existing.322_installed", before.get(rel(FDAT_ROOT / "firmware_packed.dat")) == INSTALLED322_DAT_SHA,
          "el paquete 3.22 instalado sigue intacto")
    check(checks, "existing.322_installed_fdat", before.get(rel(FDAT_ROOT / "firmware_packed.fdat")) == INSTALLED322_FDAT_SHA,
          "el .fdat 3.22 instalado sigue intacto")
    check(checks, "existing.323_recovery", before.get(rel(FDAT_ROOT / "recuperacion-323/firmware_packed.dat")) == REC323_DAT_SHA,
          "el paquete de recuperación 3.23 sigue intacto")

    exp = build_experimental(checks)
    rec = build_recovery(checks)

    # Orden de versiones (BCD: 3.22 < 3.23 < 3.24) y regla del guard.
    order = {v: int(v.split(".")[1], 16) for v in ("3.22", "3.23", "3.24")}
    check(checks, "versions.order", order["3.22"] < order["3.23"] < order["3.24"],
          "3.22 (0x22) < 3.23 (0x23) < 3.24 (0x24)")
    check(checks, "versions.experimental_gt_installed", order["3.23"] > order["3.22"],
          "3.23 > 3.22: el guard acepta la experimental (regla medida con 3.21; INFERENCIA con 3.22)")
    check(checks, "versions.recovery_gt_experimental", order["3.24"] > order["3.23"],
          "3.24 > 3.23: el guard acepta la recuperación tras la experimental")

    # Diferencias binarias entre paquetes.
    rec_fdat = read_bytes(OUT_REC / "firmware_packed.fdat")
    rec323_fdat_bytes = read_bytes(FDAT_ROOT / "recuperacion-323/firmware_packed.fdat")
    rec_dat = read_bytes(OUT_REC / "firmware_packed.dat")
    rec323_dat_bytes = read_bytes(FDAT_ROOT / "recuperacion-323/firmware_packed.dat")

    hdr_size = exp["header"]["header_size"]
    rec_fdat_ranges = diff_ranges(rec_fdat, rec323_fdat_bytes)
    rec_dat_ranges = diff_ranges(rec_dat, rec323_dat_bytes)
    dat_payload_offset = exp["container"]["payload_offset"]
    check(checks, "diff.recovery_payload_identical",
          rec_fdat[hdr_size:] == rec323_fdat_bytes[hdr_size:],
          "el cuerpo del .fdat 3.24 es idéntico al del 3.23: solo cambia la cabecera (versión y CRC)")
    check(checks, "diff.recovery_fdat_header_only",
          all(end <= hdr_size for start, end in rec_fdat_ranges) and len(rec_fdat_ranges) > 0,
          f"rangos distintos en el .fdat 3.24 vs 3.23: {rec_fdat_ranges} (cabecera = {hdr_size} B)")
    check(checks, "diff.recovery_dat_header_and_dend",
          len(rec_dat_ranges) > 0 and all(
              (dat_payload_offset <= start and end <= dat_payload_offset + 512) or (start >= len(rec_dat) - 4)
              for start, end in rec_dat_ranges),
          f"rangos distintos en el .dat 3.24 vs 3.23: {rec_dat_ranges} "
          f"(primer bloque cifrado del FDAT en {dat_payload_offset} y CRC DEND al final)")

    check(checks, "diff.packages_tar", exp["payload"]["firmware_tar_sha256"] != rec["payload"]["firmware_tar_sha256"],
          "el tar experimental (tipo 0 + B1a) difiere del tar de recuperación (oficial)")

    after = snapshot(watched)
    check(checks, "existing.unchanged", before == after,
          "los paquetes 3.22 y la recuperación 3.23 no se modificaron")

    generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    limitations = [
        ("La recuperación 3.24 solo puede instalarse si la cámara conserva acceso al actualizador "
         "(Darwin capaz de ejecutar InitCom/Upd o vía de actualizador alcanzable). No recupera un MCU "
         "que no arranca ni sustituye una recuperación independiente de Darwin."),
        "No está demostrado que un Darwin defectuoso vuelva a arrancar (E25-04 A=NO, G=NO).",
        "La aceptación del guard con 3.22 instalada es INFERENCIA: la regla se midió con 3.21 (M2).",
        ("Instalar 3.23 consume la versión; tras instalar 3.24 la siguiente prueba exigiría 3.25 y su "
         "recuperación ≥3.26 (tope 3.99). El paquete de recuperación 3.23 queda superado por el 3.24."),
        "El 3.24 restaura el Darwin oficial (3.21), no el tipo 0; volver al tipo 0 exigiría otro paquete ≥3.25.",
        "Nada de esto se ha probado en cámara: no se conectó, no se escribió RAM/NVRAM/NAND y no se flasheó.",
    ]

    exp_doc = {
        "schema": "a6000.e25_05.manifest.v1",
        "generated_by": "scripts/e25_05/build_packages.py",
        "generated_at": generated_at,
        "base_commit": BASE_COMMIT,
        "role": "experimental",
        "version": "3.23",
        "install_order": 1,
        "scope": "offline: sin cámara, sin USB, sin RAM/NVRAM/NAND, sin flasheo",
        "preconditions": {
            "installed_version": "3.22",
            "installed_darwin": "tipo 0",
            "guard": "solo acepta versión estrictamente mayor que la instalada (medido con 3.21; INFERENCIA con 3.22)",
        },
        "dir": rel(OUT_EXP),
        "outputs": {k: exp[k] for k in ("config", "fdat", "dat", "header", "container", "payload", "darwin")},
        "tar_members_changed_vs_official": exp["tar_members_changed_vs_official"],
        "differences": {
            "b1a_vs_tipo0": "exactamente 2 bytes en 0x1fe6a (28 46 -> 0a e0); ver analysis/e25-05/diferencias-binarias.json",
            "tar_vs_official": list(DARWIN_FILES),
        },
        "checks": checks[:],
        "limitations": limitations,
    }
    rec_doc = {
        "schema": "a6000.e25_05.manifest.v1",
        "generated_by": "scripts/e25_05/build_packages.py",
        "generated_at": generated_at,
        "base_commit": BASE_COMMIT,
        "role": "recovery",
        "version": "3.24",
        "install_order": 2,
        "scope": "offline: sin cámara, sin USB, sin RAM/NVRAM/NAND, sin flasheo",
        "preconditions": {
            "installed_version": "3.23 (experimental)",
            "installed_darwin": "tipo 0 + B1a",
            "guard": "solo acepta versión estrictamente mayor que la instalada (3.24 > 3.23)",
        },
        "dir": rel(OUT_REC),
        "outputs": {k: rec[k] for k in ("config", "fdat", "dat", "header", "container", "payload", "reused_from")},
        "differences": {
            "payload_vs_recovery_323": "firmware.tar y updater.img idénticos (oficiales); solo cambia la versión de cabecera",
            "fdat_ranges_vs_recovery_323": rec_fdat_ranges,
            "dat_ranges_vs_recovery_323": rec_dat_ranges,
        },
        "checks": checks[:],
        "limitations": limitations,
    }
    write_manifest(MANI_DIR / "manifest-experimental-323.json", exp_doc)
    write_manifest(MANI_DIR / "manifest-recuperacion-324.json", rec_doc)

    original_core = read_bytes(FW / "firmware.tar_unpacked/0640_darwin/darwin_core.bin")
    diffs = {
        "schema": "a6000.e25_05.differences.v1",
        "generated_by": "scripts/e25_05/build_packages.py",
        "generated_at": generated_at,
        "base_commit": BASE_COMMIT,
        "b1a_vs_tipo0": {
            "tipo0_sha256": TIPO0_CORE_SHA,
            "b1a_sha256": B1A_CORE_SHA,
            "count": len(exp["darwin"]["diff_vs_tipo0"]),
            "bytes": exp["darwin"]["diff_vs_tipo0"],
            "note": "2 bytes: 0x1fe6a 28 46 -> 0a e0 (B.N a 0x1fe82); el resto del tipo 0 queda intacto",
        },
        "b1a_vs_original": {
            "original_sha256": OFFICIAL_CORE_SHA,
            "count": len(diff_positions(original_core, read_bytes(ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin"))),
            "bytes": diff_positions(original_core, read_bytes(ROOT / "analysis/e25/darwin_core_tipo0_sin_rearme.bin")),
            "note": "filtro tipo 0 en 0x20c78..0x20c7f + 2 bytes de la compuerta en 0x1fe6a..0x1fe6b",
        },
        "packages": {
            "experimental_323_tar_sha256": exp["payload"]["firmware_tar_sha256"],
            "recuperacion_324_tar_sha256": rec["payload"]["firmware_tar_sha256"],
            "experimental_vs_recovery_tar_members_changed": list(DARWIN_FILES),
            "recovery_324_fdat_diff_ranges_vs_323": rec_fdat_ranges,
            "recovery_324_dat_diff_ranges_vs_323": rec_dat_ranges,
            "recovery_324_fdat_sha256": rec["fdat"]["sha256"],
            "recovery_324_dat_sha256": rec["dat"]["sha256"],
            "experimental_323_fdat_sha256": exp["fdat"]["sha256"],
            "experimental_323_dat_sha256": exp["dat"]["sha256"],
        },
    }
    write_manifest(MANI_DIR / "diferencias-binarias.json", diffs)

    package_checksums(OUT_EXP)
    package_checksums(OUT_REC)

    print(json.dumps({
        "experimental": {"dir": rel(OUT_EXP), "fdat_sha256": exp["fdat"]["sha256"], "dat_sha256": exp["dat"]["sha256"]},
        "recovery": {"dir": rel(OUT_REC), "fdat_sha256": rec["fdat"]["sha256"], "dat_sha256": rec["dat"]["sha256"]},
        "checks": len(checks),
        "failed": sum(1 for c in checks if c["result"] != "PASS"),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
