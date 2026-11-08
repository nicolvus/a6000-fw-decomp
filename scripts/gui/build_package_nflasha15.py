#!/usr/bin/env python3
"""Empaqueta una `nflasha15` nueva en un firmware.tar existente y genera FDAT/DAT (G08/G09). NO instala nada.

Pasos: sustituir `0700_part_image/dev/nflasha15` y su línea de `part_image.sum` (CRC-32 + tamaño) en el tar base → `fwtool`
(`e25_05.build_packages`) con la versión pedida (el actualizador solo acepta versiones mayores) → desempaquetar y comprobar que el
tar, el `nflasha15` y la suma verifican byte a byte.
Uso: build_package_nflasha15.py NFLASHA15_NUEVO SALIDA [--base-tar TAR] [--version 3.39]
La base por defecto es el CFW 3.38 (`analysis/e25-27/artifacts-338/firmware.integrated.tar`: EFCS desactivado = electrónico).
"""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_05 import build_packages as B
from e25_27 import build, sums, tarball, tpzl

NFLASHA15 = "0700_part_image/dev/nflasha15"
ENTRY = "dev/nflasha15"
FW = ROOT / "firmware/extracted/fw321"
DEFAULT_BASE = ROOT / "analysis/e25-27/artifacts-338/firmware.integrated.tar"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(new15: Path, out: Path, base_tar: Path, version: str, darwin_v3: bool = False) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    blob, base = new15.read_bytes(), base_tar.read_bytes()
    entries, _ = tarball.parse(base)
    members = {e.name: e.data for e in entries}
    part_sum, detail = sums.update(members[build.PART_SUM].decode("ascii"), ENTRY, blob)
    assert sums.verify(part_sum, ENTRY, blob)
    repl = {NFLASHA15: blob, build.PART_SUM: part_sum.encode("ascii")}
    if darwin_v3:  # R82/R83: tabla EFCS por velocidad en Darwin (neutra con la tabla NVRAM a ceros)
        core, _ = build.efcs_tabla_diff(members[build.DARWIN_CORE])
        dsum, _ = build._sum_text_with_core(members[build.DARWIN_SUM].decode("ascii"), core)
        repl |= {build.DARWIN_CORE: core, build.DARWIN_SUM: dsum.encode("ascii")}
    tar_bytes, _ = tarball.rebuild(base, repl)
    tar_path = out / "firmware.tar"
    tar_path.write_bytes(tar_bytes)
    cfg = out / f"config-{version.replace('.', '')}.yaml"
    cfg.write_text(build._config_text((FW / "config.yaml").read_text(), version), encoding="utf-8")
    pkg = out / f"package-{version}"
    pkg.mkdir(exist_ok=True)
    B.pack(cfg, tar_path, FW / "updater.img", pkg)
    header = B.header_of(pkg / "firmware_packed.fdat")
    assert header["version"] == version and header["model"] == f"0x{build.MODEL:08x}", header
    with tempfile.TemporaryDirectory() as tmp:
        B.unpack(pkg / "firmware_packed.dat", Path(tmp))
        got = (Path(tmp) / "firmware.tar").read_bytes()
        assert sha(got) == sha(tar_bytes), "el tar extraído no coincide"
        got_members = {e.name: e.data for e in tarball.parse(got)[0]}
        assert all(got_members[k] == v for k, v in repl.items()) and got_members[NFLASHA15] == blob and sums.verify(got_members[build.PART_SUM].decode("ascii"), ENTRY, blob)
        assert tpzl.TpzlImage.parse(got_members[NFLASHA15]).decompressed()[1080:1082] == b"\x53\xef"  # firma ext2 (superbloque)
        for name, data in members.items():  # el resto de miembros, intacto
            if name not in repl:
                assert got_members[name] == data, name
    B.package_checksums(pkg)
    result = {"version": version, "darwin_v3": darwin_v3, "base_tar": str(base_tar), "tar_sha256": sha(tar_bytes), "part_sum_linea": detail["line_after"],
              "dat": str(pkg / "firmware_packed.dat"), "dat_sha256": B.sha256(pkg / "firmware_packed.dat"),
              "estado": "CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA"}
    (out / "container.json").write_text(json.dumps(result, indent=1))
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("nflasha15", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--base-tar", type=Path, default=DEFAULT_BASE)
    ap.add_argument("--version", default="3.39")
    ap.add_argument("--darwin-v3", action="store_true", help="añade el parche EFCS v3 de Darwin (R82, commit 20b33eed)")
    a = ap.parse_args()
    print(json.dumps(main(a.nflasha15, a.salida, a.base_tar, a.version, a.darwin_v3), indent=1))
