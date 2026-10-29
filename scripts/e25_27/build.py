"""E25-27 — constructor reproducible del firmware integrado EFCS / Electronic.

Entradas (originales de Sony, verificadas por SHA-256):

    firmware/extracted/fw321/firmware.tar   (3.21, modelo 0x41030035, región 0)
    firmware/extracted/fw321/updater.img

Salidas (por defecto en `analysis/e25-27/artifacts/`, ignorado por Git):

    av-cam.integrated.bin          BIONZ con selector + C3-B
    darwin_core.integrated.bin     Darwin con la compuerta por captura
    nflasha3.integrated.bin        partición TPZL recompuesta (solo 3 bloques)
    firmware.integrated.tar        tar con los cuatro miembros actualizados
    firmware_packed.fdat / .dat    contenedor experimental 3.25 (con --package)
    manifest.json / container.json

El constructor rechaza cualquier entrada que no sea el original exacto, detecta
solapamientos de cuevas, comprueba que no hay cambios fuera del manifiesto y
verifica la reversión byte a byte.  No instala, no flashea y no toca la cámara.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD
from e25_26 import patch_c3b as PC

from e25_27 import fatimg, sums, tarball, tpzl

FW = ROOT / "firmware/extracted/fw321"
DEFAULT_TAR = FW / "firmware.tar"
DEFAULT_UPDATER = FW / "updater.img"
DEFAULT_OUT = ROOT / "analysis/e25-27/artifacts"

TAR_SHA256 = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
UPDATER_SHA256 = "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
AVCAM_SHA256 = PB.SHA256
DARWIN_SHA256 = PD.SHA256

NFLASHA3 = "0700_part_image/dev/nflasha3"
PART_SUM = "0701_part_image_sum/part_image.sum"
DARWIN_CORE = "0640_darwin/darwin_core.bin"
DARWIN_SUM = "0641_darwin_sum/darwin.sum"
AVCAM_NAME = "AV-CAM.BIN"
PART_ENTRY = "dev/nflasha3"

VERSION = "3.25"
MODEL = 0x41030035
REGION = 0

STATUS = "CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA"


class BuildError(ValueError):
    """Entrada incompatible, conflicto de regiones o verificación fallida."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path) -> bytes:
    if not path.is_file():
        raise BuildError(f"no existe: {path}")
    return path.read_bytes()


@dataclass(frozen=True)
class Originals:
    tar_path: Path
    updater_path: Path
    tar: bytes
    updater: bytes
    members: dict[str, bytes]
    partition: tpzl.TpzlImage
    fat: fatimg.Fat16
    avcam: bytes
    darwin: bytes
    darwin_sum: str
    part_sum: str

    @property
    def avcam_sha256(self) -> str:
        return sha256(self.avcam)

    @property
    def darwin_sha256(self) -> str:
        return sha256(self.darwin)


def load_originals(tar_path: Path = DEFAULT_TAR, updater_path: Path = DEFAULT_UPDATER) -> Originals:
    tar = _read(tar_path)
    updater = _read(updater_path)
    if sha256(tar) != TAR_SHA256:
        raise BuildError(f"firmware.tar no es el original 3.21: {sha256(tar)}")
    if sha256(updater) != UPDATER_SHA256:
        raise BuildError(f"updater.img no es el original: {sha256(updater)}")
    entries, _ = tarball.parse(tar)
    members = {entry.name: entry.data for entry in entries}
    for name in (NFLASHA3, PART_SUM, DARWIN_CORE, DARWIN_SUM):
        if name not in members:
            raise BuildError(f"falta el miembro {name}")
    partition = tpzl.TpzlImage.parse(members[NFLASHA3])
    fat = fatimg.Fat16.parse(partition.decompressed())
    avcam = fat.read(AVCAM_NAME)
    darwin = members[DARWIN_CORE]
    if sha256(avcam) != AVCAM_SHA256:
        raise BuildError(f"av-cam.bin inesperado: {sha256(avcam)}")
    if sha256(darwin) != DARWIN_SHA256:
        raise BuildError(f"darwin_core.bin inesperado: {sha256(darwin)}")
    if len(avcam) != PB.SIZE or len(darwin) != PD.SIZE:
        raise BuildError("tamaños de entrada inesperados")
    return Originals(
        tar_path=tar_path,
        updater_path=updater_path,
        tar=tar,
        updater=updater,
        members=members,
        partition=partition,
        fat=fat,
        avcam=avcam,
        darwin=darwin,
        darwin_sum=members[DARWIN_SUM].decode("ascii"),
        part_sum=members[PART_SUM].decode("ascii"),
    )


def _diff_addresses(diff: list[dict]) -> set[int]:
    return {item["address"] for item in diff}


def apply_patches(avcam: bytes, darwin: bytes) -> dict[str, Any]:
    """Aplica selector, C3-B y la compuerta Darwin sobre los originales exactos."""
    if sha256(avcam) != AVCAM_SHA256:
        raise BuildError("BIONZ de entrada no es el original (¿ya parcheado?)")
    if sha256(darwin) != DARWIN_SHA256:
        raise BuildError("Darwin de entrada no es el original (¿tipo 0/B1a?)")

    selector, diff_selector = PB.apply_bytes(avcam)
    combined, diff_c3b = PC.apply_bytes(selector)
    darwin_out, diff_darwin = PD.apply_bytes(darwin)

    if _diff_addresses(diff_selector) & _diff_addresses(diff_c3b):
        raise BuildError("selector y C3-B comparten bytes")
    if not _diff_addresses(diff_selector) <= PB.allowed_addresses():
        raise BuildError("el selector cambia bytes no autorizados")
    if not _diff_addresses(diff_c3b) <= PC.allowed_addresses():
        raise BuildError("C3-B cambia bytes no autorizados")
    if not _diff_addresses(diff_darwin) <= PD.allowed_addresses():
        raise BuildError("Darwin cambia bytes no autorizados")

    if PB.CAVE + PB.CAVE_LEN > PC.CAVE:
        raise BuildError("cueva del selector y C3-B solapadas")
    if PC.CAVE + PC.CAVE_LEN > 0x435418D8:
        raise BuildError("C3-B invade la cola de metadatos de la cabecera")
    if not all(b == 0 for b in avcam[PC.CAVE - PB.BASE:PC.CAVE - PB.BASE + PC.CAVE_LEN]):
        raise BuildError("la cueva C3-B no estaba libre")

    if PB.restore_bytes(selector) != avcam:
        raise BuildError("reversión del selector fallida")
    if PC.restore_bytes(combined) != selector:
        raise BuildError("reversión de C3-B fallida")
    if PD.restore_bytes(darwin_out) != darwin:
        raise BuildError("reversión de Darwin fallida")

    return {
        "bionz": combined,
        "darwin": darwin_out,
        "selector": selector,
        "diff_selector": diff_selector,
        "diff_c3b": diff_c3b,
        "diff_darwin": diff_darwin,
    }


def _sum_text_with_core(template: str, core: bytes) -> tuple[str, dict]:
    """Reescribe `darwin.sum` con el CRC-32 y el tamaño del core integrado."""
    return sums.update(template, "darwin_core.bin", core)


def build_tar(originals: Originals, built: dict[str, Any]) -> dict[str, Any]:
    """Recompone nflasha3, actualiza part_image.sum y reconstruye firmware.tar."""
    fat, fat_info = originals.fat.patch(AVCAM_NAME, built["bionz"])
    partition_bytes, block_info = tpzl.patch_decompressed(originals.partition, fat)

    check_fat = fatimg.Fat16.parse(tpzl.TpzlImage.parse(partition_bytes).decompressed())
    if check_fat.read(AVCAM_NAME) != built["bionz"]:
        raise BuildError("la partición no reproduce el BIONZ integrado")

    part_sum, part_sum_info = sums.update(originals.part_sum, PART_ENTRY, partition_bytes)
    if not sums.verify(part_sum, PART_ENTRY, partition_bytes):
        raise BuildError("part_image.sum no verifica")

    darwin_sum, darwin_sum_info = _sum_text_with_core(originals.darwin_sum, built["darwin"])

    replacements = {
        NFLASHA3: partition_bytes,
        PART_SUM: part_sum.encode("ascii"),
        DARWIN_CORE: built["darwin"],
        DARWIN_SUM: darwin_sum.encode("ascii"),
    }
    tar_bytes, tar_info = tarball.rebuild(originals.tar, replacements)

    entries, _ = tarball.parse(tar_bytes)
    check = {entry.name: entry.data for entry in entries}
    if check[NFLASHA3] != partition_bytes or check[DARWIN_CORE] != built["darwin"]:
        raise BuildError("el tar reconstruido no contiene las imágenes previstas")
    if check[PART_SUM] != part_sum.encode("ascii") or check[DARWIN_SUM] != darwin_sum.encode("ascii"):
        raise BuildError("el tar reconstruido no contiene las sumas previstas")

    return {
        "tar": tar_bytes,
        "partition": partition_bytes,
        "part_sum": part_sum,
        "darwin_sum": darwin_sum,
        "fat_info": fat_info,
        "block_info": block_info,
        "part_sum_info": part_sum_info,
        "darwin_sum_info": darwin_sum_info,
        "tar_info": tar_info,
    }


def binary_manifest(originals: Originals, built: dict[str, Any], out: dict[str, Any]) -> dict[str, Any]:
    diff_all = built["diff_selector"] + built["diff_c3b"] + built["diff_darwin"]
    return {
        "phase": "E25-27",
        "status": STATUS,
        "installable": False,
        "experimental": True,
        "version": VERSION,
        "model": f"0x{MODEL:08x}",
        "region": REGION,
        "inputs": {
            "firmware_tar": {"path": str(originals.tar_path), "sha256": sha256(originals.tar),
                             "size": len(originals.tar)},
            "updater_img": {"path": str(originals.updater_path), "sha256": sha256(originals.updater),
                            "size": len(originals.updater)},
            "av-cam.bin": {"sha256": originals.avcam_sha256, "size": len(originals.avcam),
                           "container": NFLASHA3, "fat_name": AVCAM_NAME},
            "darwin_core.bin": {"sha256": originals.darwin_sha256, "size": len(originals.darwin),
                                "container": DARWIN_CORE},
        },
        "outputs": {
            "av-cam.bin": {"sha256": sha256(built["bionz"]), "size": len(built["bionz"])},
            "darwin_core.bin": {"sha256": sha256(built["darwin"]), "size": len(built["darwin"])},
            "nflasha3": {"sha256": sha256(out["partition"]), "size": len(out["partition"])},
            "firmware.tar": {"sha256": sha256(out["tar"]), "size": len(out["tar"])},
        },
        "components": {
            "selector": {
                "cave": hex(PB.CAVE), "length": PB.CAVE_LEN,
                "sites": [{"address": hex(a), "before": o.hex(), "after": n.hex(), "role": r}
                          for a, o, n, r in PB.PATCHES],
                "diff_count": len(built["diff_selector"]),
            },
            "c3b": {
                "hook": hex(PC.HOOK), "cave": hex(PC.CAVE), "length": PC.CAVE_LEN,
                "sites": [{"address": hex(PC.HOOK), "before": PC.HOOK_OLD.hex(),
                           "after": PC.hook_bytes().hex(), "role": "bl imager -> bl cueva C3-B"},
                          {"address": hex(PC.CAVE), "length": PC.CAVE_LEN,
                           "bytes": PC.cave_bytes().hex(), "role": "cueva C3-B"}],
                "diff_count": len(built["diff_c3b"]),
                "conditions": ["paso 0", "cap+0x41c == 1", "r7 (svd) <= 1", "VTS != 0",
                               "shd > VTS si svd == 1", "shd' < VTS"],
            },
            "darwin": {
                "cave": hex(PD.CAVE), "length": PD.CAVE_LEN,
                "flag": hex(PD.FLAG_ADDR),
                "sites": [{"address": hex(a), "before": o.hex(), "after": n.hex(), "role": r}
                          for a, o, n, r in PD.PATCHES],
                "diff_count": len(built["diff_darwin"]),
            },
        },
        "diff": diff_all,
        "diff_count": len(diff_all),
        "cave_overlap": {
            "selector_end": hex(PB.CAVE + PB.CAVE_LEN),
            "c3b_start": hex(PC.CAVE),
            "c3b_end": hex(PC.CAVE + PC.CAVE_LEN),
            "header_metadata_tail": "0x435418d8",
            "overlap": False,
        },
        "protection": {
            "bionz": [name for name, _, _ in PB.PROTECTED],
            "darwin": [name for name, _, _ in PD.PROTECTED],
            "note": "las regiones protegidas se comparan por SHA-256 en cada parche",
        },
        "partition": {
            "container": NFLASHA3,
            "tpzl_blocks": len(originals.partition.entries),
            "block_log2": originals.partition.block_log2,
            "fat_offset": out["fat_info"]["first_cluster_offset"],
            "changed_blocks": [b["block"] for b in out["block_info"] if b["recompressed"]],
            "blocks": out["block_info"],
            "part_sum": out["part_sum_info"],
        },
        "tar": {
            "members": len(tarball.parse(out["tar"])[0]),
            "replacements": out["tar_info"],
            "darwin_sum": out["darwin_sum_info"],
        },
        "reversal": {
            "bionz": "PB.restore_bytes -> selector; PC.restore_bytes -> original; SHA-256 "
                     + AVCAM_SHA256,
            "darwin": "PD.restore_bytes -> original; SHA-256 " + DARWIN_SHA256,
            "partition": "reconstruir firmware.tar desde el original verificado; el original "
                         "se conserva intacto en la entrada",
            "verified": True,
        },
        "limitations": [
            "No se ha ejecutado en la cámara ni se ha instalado.",
            "El fin electrónico de integración y la ausencia de movimiento no están demostrados.",
            "La ruta larga (>= 1/15 s) no está incluida en C3-B.",
            "cap+0x73b conserva el valor calculado con el ShutMode nativo (E25-28).",
            "La recuperación de un Darwin que no arranque sigue sin demostrarse (E24-04).",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                    encoding="utf-8")


def build(out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    originals = load_originals()
    built = apply_patches(originals.avcam, originals.darwin)
    out = build_tar(originals, built)
    manifest = binary_manifest(originals, built, out)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "av-cam.integrated.bin").write_bytes(built["bionz"])
    (out_dir / "darwin_core.integrated.bin").write_bytes(built["darwin"])
    (out_dir / "nflasha3.integrated.bin").write_bytes(out["partition"])
    (out_dir / "firmware.integrated.tar").write_bytes(out["tar"])
    (out_dir / "part_image.integrated.sum").write_text(out["part_sum"], encoding="ascii")
    (out_dir / "darwin.integrated.sum").write_text(out["darwin_sum"], encoding="ascii")
    write_json(out_dir / "manifest.json", manifest)
    return manifest


def _config_text(template: str, version: str) -> str:
    import yaml  # type: ignore[import-untyped]

    text = template.replace("version: '3.21'", f"version: '{version}'")
    if text == template:
        raise BuildError("no se encontró la versión 3.21 en la plantilla")
    parsed = yaml.safe_load(text)
    expected = {"isAccessory": False, "model": MODEL, "region": REGION, "version": version}
    if parsed["fdat"] != expected:
        raise BuildError(f"config inesperada: {parsed['fdat']}")
    if parsed["dat"]["crypterName"] != "CXD90014" or parsed["dat"]["isLens"]:
        raise BuildError("config: crypter/isLens inesperados")
    return text


def package(out_dir: Path = DEFAULT_OUT, version: str = VERSION) -> dict[str, Any]:
    """Empaqueta FDAT/DAT con fwtool y verifica la extracción inversa."""
    from e25_05 import build_packages as B

    originals = load_originals()
    tar_path = out_dir / "firmware.integrated.tar"
    if not tar_path.is_file():
        raise BuildError("falta firmware.integrated.tar; ejecuta build() primero")
    tar_bytes = tar_path.read_bytes()
    config_text = _config_text((FW / "config.yaml").read_text(), version)
    config_path = out_dir / f"config-{version.replace('.', '')}.yaml"
    config_path.write_text(config_text, encoding="utf-8")

    pkg_dir = out_dir / f"package-{version}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    B.pack(config_path, tar_path, originals.updater_path, pkg_dir)

    fdat = pkg_dir / "firmware_packed.fdat"
    dat = pkg_dir / "firmware_packed.dat"
    header = B.header_of(fdat)
    container = B.dat_info(dat)
    if header["version"] != version or header["model"] != f"0x{MODEL:08x}":
        raise BuildError(f"cabecera inesperada: {header}")
    if header["region"] != REGION or header["mode"] != "U" or header["luw"] != "N":
        raise BuildError(f"modo/región inesperados: {header}")
    if container["updater_usb_descriptors"] != [[0x54C, 0x3E2]] or container["is_lens"]:
        raise BuildError(f"contenedor inesperado: {container}")

    with tempfile.TemporaryDirectory(prefix="e25-27-verify-") as tmp:
        B.unpack(dat, Path(tmp))
        got_tar = (Path(tmp) / "firmware.tar").read_bytes()
        got_updater = (Path(tmp) / "updater.img").read_bytes()
        got_config = (Path(tmp) / "config.yaml").read_text()
        if sha256(got_tar) != sha256(tar_bytes):
            raise BuildError("el tar extraído no coincide con el empaquetado")
        if sha256(got_updater) != UPDATER_SHA256:
            raise BuildError("el updater extraído no coincide")
        if f"version: '{version}'" not in got_config:
            raise BuildError("la config extraída no declara la versión")

        entries, _ = tarball.parse(got_tar)
        members = {entry.name: entry.data for entry in entries}
        part = tpzl.TpzlImage.parse(members[NFLASHA3])
        fat = fatimg.Fat16.parse(part.decompressed())
        avcam = fat.read(AVCAM_NAME)
        if sha256(avcam) != sha256((out_dir / "av-cam.integrated.bin").read_bytes()):
            raise BuildError("el av-cam extraído no coincide con el construido")
        if sha256(members[DARWIN_CORE]) != sha256((out_dir / "darwin_core.integrated.bin").read_bytes()):
            raise BuildError("el Darwin extraído no coincide con el construido")
        if not sums.verify(members[PART_SUM].decode("ascii"), PART_ENTRY, members[NFLASHA3]):
            raise BuildError("part_image.sum extraído no verifica")

    result = {
        "phase": "E25-27",
        "status": STATUS,
        "installable": False,
        "version": version,
        "config": {"path": str(config_path), "sha256": sha256(config_text.encode())},
        "fdat": {"path": str(fdat), "sha256": B.sha256(fdat), "size": fdat.stat().st_size},
        "dat": {"path": str(dat), "sha256": B.sha256(dat), "size": dat.stat().st_size},
        "header": header,
        "container": container,
        "tar_sha256": sha256(tar_bytes),
        "roundtrip": {
            "tar_extracted_sha256": sha256(got_tar),
            "avcam_extracted_sha256": sha256(avcam),
            "darwin_extracted_sha256": sha256(members[DARWIN_CORE]),
            "part_sum_verified": True,
        },
    }
    write_json(out_dir / "container.json", result)
    return result


def restore(out_dir: Path = DEFAULT_OUT) -> dict[str, Any]:
    """Revierte los binarios integrados y comprueba los SHA-256 originales."""
    originals = load_originals()
    bionz = (out_dir / "av-cam.integrated.bin").read_bytes()
    darwin = (out_dir / "darwin_core.integrated.bin").read_bytes()
    selector = PC.restore_bytes(bionz)
    avcam = PB.restore_bytes(selector)
    darwin_orig = PD.restore_bytes(darwin)
    ok = sha256(avcam) == AVCAM_SHA256 and sha256(darwin_orig) == DARWIN_SHA256
    (out_dir / "av-cam.restored.bin").write_bytes(avcam)
    (out_dir / "darwin_core.restored.bin").write_bytes(darwin_orig)
    payload = {
        "phase": "E25-27",
        "action": "restore",
        "bionz": {"integrated_sha256": sha256(bionz), "restored_sha256": sha256(avcam),
                  "original_sha256": AVCAM_SHA256},
        "darwin": {"integrated_sha256": sha256(darwin), "restored_sha256": sha256(darwin_orig),
                   "original_sha256": DARWIN_SHA256},
        "firmware_tar_original_sha256": sha256(originals.tar),
        "verified": ok,
    }
    write_json(out_dir / "restore.json", payload)
    if not ok:
        raise BuildError("la reversión no reproduce los originales")
    return payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--package", action="store_true", help="empaquetar FDAT/DAT y verificar")
    ap.add_argument("--restore", action="store_true", help="revertir y verificar los originales")
    ap.add_argument("--version", default=VERSION)
    args = ap.parse_args(argv)
    manifest = build(args.out)
    print(json.dumps({
        "status": manifest["status"],
        "outputs": manifest["outputs"],
        "changed_blocks": manifest["partition"]["changed_blocks"],
    }, indent=2, ensure_ascii=False))
    if args.package:
        print(json.dumps(package(args.out, args.version), indent=2, ensure_ascii=False))
    if args.restore:
        print(json.dumps(restore(args.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
