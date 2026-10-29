"""E25-27 — evidencia versionable de la construcción integrada (sin binarios).

Lee los artefactos locales (ignorados por Git), ejecuta la emulación integrada y
escribe `analysis/e25-27/evidence.json` con hashes, parches, partición, contenedor,
matriz de modos/velocidades y el rastro estático de `cap+0x73b`.

Uso:
    .venv/bin/python scripts/e25_27/build_evidence.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import capstone
from e25_24 import patch_bionz as PB
from e25_24 import patch_darwin as PD
from e25_26 import patch_c3b as PC

from e25_27 import build, emu, fatimg, sums, tarball, tpzl

ARTIFACTS = ROOT / "analysis/e25-27/artifacts"
OUT = ROOT / "analysis/e25-27/evidence.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def trace_73b(avcam: bytes) -> list[dict[str, str]]:
    """Instrucciones que leen o escriben `cap+0x73b` (barrido lineal Thumb)."""
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.skipdata = True
    hits = []
    for ins in md.disasm(avcam, PB.BASE):
        if "0x73b" in ins.op_str:
            hits.append({
                "address": hex(ins.address),
                "mnemonic": ins.mnemonic,
                "operands": ins.op_str,
                "kind": "write" if ins.mnemonic.startswith("str") else "read",
            })
    return hits


def independent_container_audit() -> dict[str, Any] | None:
    """Audita el .dat/.fdat con los parsers propios de E25-06 (no fwtool)."""
    pkg = ARTIFACTS / f"package-{build.VERSION}"
    dat = pkg / "firmware_packed.dat"
    fdat = pkg / "firmware_packed.fdat"
    if not dat.is_file() or not fdat.is_file():
        return None
    import mmap

    import e25_06.audit_packages as A  # type: ignore[import-not-found]

    raw = fdat.read_bytes()
    keys = A.load_keys()
    with dat.open("rb") as fh:
        buf = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        info = A.parse_dat(buf)
        dec = A.decrypt_fdat(buf, info["fdat_offset"], info["fdat_size"], keys, compare=raw)
        header = A.parse_fdat_header(raw[:512])
        tar = raw[header["firmware_offset"]:header["firmware_offset"] + header["firmware_size"]]
        parsed = A.parse_tar(tar)
        return {
            "dat_magic": info["magic_ok"],
            "dend_stored": info["dend_stored"],
            "dend_computed": info["dend_computed"],
            "blocks": dec.blocks,
            "bad_sum": dec.bad_sum,
            "bad_flag": dec.bad_flag,
            "bad_len": dec.bad_len,
            "pad_not_ff": dec.pad_not_ff,
            "plain_size": dec.plain_size,
            "fdat_size": len(raw),
            "plaintext_matches_fdat": dec.first_mismatch_vs_fdat is None,
            "header": {
                "version": header["version"],
                "model": f"0x{header['model']:08x}",
                "checksum_stored": header["checksum_stored"],
                "checksum_computed": header["checksum_computed"],
                "mode": header["mode"],
                "luw": header["luw"],
                "num_filesystems": header["num_filesystems"],
            },
            "tar_members": len(parsed["members"]),
            "tar_problems": parsed["problems"],
            "ok": (
                info["magic_ok"]
                and info["dend_stored"] == info["dend_computed"]
                and not dec.bad_sum and not dec.bad_flag and not dec.bad_len
                and dec.first_mismatch_vs_fdat is None
                and header["checksum_stored"] == header["checksum_computed"]
                and not parsed["problems"]
            ),
        }


def main() -> int:
    originals = build.load_originals()
    built = build.apply_patches(originals.avcam, originals.darwin)
    rebuilt = build.build_tar(originals, built)

    avcam_out = built["bionz"]
    darwin_out = built["darwin"]
    partition = rebuilt["partition"]
    tar_bytes = rebuilt["tar"]

    part = tpzl.TpzlImage.parse(partition)
    fat = fatimg.Fat16.parse(part.decompressed())
    entries, _ = tarball.parse(tar_bytes)
    members = {entry.name: entry.data for entry in entries}

    emu_result = emu.matrix(avcam_out, darwin_out, originals.avcam)
    container: dict[str, Any] | None = None
    if (ARTIFACTS / "container.json").is_file():
        container = json.loads((ARTIFACTS / "container.json").read_text())
        for key in ("config", "fdat", "dat"):
            if key in container and "path" in container[key]:
                container[key]["path"] = str(Path(container[key]["path"]).relative_to(ROOT))

    payload: dict[str, Any] = {
        "phase": "E25-27",
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": build.STATUS,
        "installable": False,
        "version": build.VERSION,
        "command": "python scripts/e25_27/build.py --package && "
                   "python scripts/e25_27/build_evidence.py",
        "inputs": {
            "firmware_tar": {"sha256": sha256(originals.tar), "size": len(originals.tar),
                             "version": "3.21"},
            "updater_img": {"sha256": sha256(originals.updater), "size": len(originals.updater)},
            "av-cam.bin": {"sha256": originals.avcam_sha256, "size": len(originals.avcam)},
            "darwin_core.bin": {"sha256": originals.darwin_sha256, "size": len(originals.darwin)},
        },
        "outputs": {
            "av-cam.bin": {"sha256": sha256(avcam_out), "size": len(avcam_out)},
            "darwin_core.bin": {"sha256": sha256(darwin_out), "size": len(darwin_out)},
            "nflasha3": {"sha256": sha256(partition), "size": len(partition)},
            "firmware.tar": {"sha256": sha256(tar_bytes), "size": len(tar_bytes)},
            "part_image.sum": {"sha256": sha256(members[build.PART_SUM])},
            "darwin.sum": {"sha256": sha256(members[build.DARWIN_SUM])},
        },
        "patches": {
            "selector": {
                "cave": hex(PB.CAVE), "length": PB.CAVE_LEN,
                "diff_count": len(built["diff_selector"]),
                "sites": [hex(a) for a, _, _, _ in PB.PATCHES],
            },
            "c3b": {
                "hook": hex(PC.HOOK), "cave": hex(PC.CAVE), "length": PC.CAVE_LEN,
                "diff_count": len(built["diff_c3b"]),
            },
            "darwin": {
                "cave": hex(PD.CAVE), "length": PD.CAVE_LEN,
                "diff_count": len(built["diff_darwin"]),
                "sites": [hex(a) for a, _, _, _ in PD.PATCHES],
            },
            "total_diff": len(built["diff_selector"]) + len(built["diff_c3b"]) + len(built["diff_darwin"]),
            "overlap": False,
            "cave_layout": {
                "selector": [hex(PB.CAVE), hex(PB.CAVE + PB.CAVE_LEN)],
                "c3b": [hex(PC.CAVE), hex(PC.CAVE + PC.CAVE_LEN)],
                "header_metadata_tail": "0x435418d8",
            },
        },
        "reversal": {
            "bionz": "PC.restore_bytes -> PB.restore_bytes",
            "darwin": "PD.restore_bytes",
            "bionz_original_sha256": PB.SHA256,
            "darwin_original_sha256": PD.SHA256,
            "verified": (
                PB.restore_bytes(PC.restore_bytes(avcam_out)) == originals.avcam
                and PD.restore_bytes(darwin_out) == originals.darwin
            ),
        },
        "partition": {
            "container": build.NFLASHA3,
            "tpzl_blocks": len(part.entries),
            "block_log2": part.block_log2,
            "fat_type": fat.fat_type,
            "fat_name": build.AVCAM_NAME,
            "fat_first_cluster_offset": hex(fat.cluster_offset(fat.find(build.AVCAM_NAME).clusters[0])),
            "changed_blocks": [b["block"] for b in rebuilt["block_info"] if b["recompressed"]],
            "blocks": [b for b in rebuilt["block_info"] if b["recompressed"]],
            "part_sum": rebuilt["part_sum_info"],
            "roundtrip_avcam_sha256": sha256(fat.read(build.AVCAM_NAME)),
            "part_sum_verified": sums.verify(
                members[build.PART_SUM].decode("ascii"), build.PART_ENTRY, members[build.NFLASHA3]
            ),
        },
        "tar": {
            "members": len(entries),
            "changed": [item["name"] for item in rebuilt["tar_info"]],
            "darwin_sum": rebuilt["darwin_sum_info"],
        },
        "emulation": {
            "all_ok": emu_result["all_ok"],
            "efcs_identical": emu_result["efcs_identical"],
            "electronic_normalized": emu_result["electronic_normalized"],
            "electronic_pred0_ok": emu_result["electronic_pred0_ok"],
            "alternation_ok": emu_result["alternation_ok"],
            "errors_ok": emu_result["errors_ok"],
            "invalid_field_ok": emu_result["invalid_field_ok"],
            "speeds_ok": emu_result["speeds_ok"],
            "efcs": emu_result["efcs"],
            "electronic": emu_result["electronic"],
            "alternation": emu_result["alternation"],
            "errors": {
                k: {"shd": v["shd_SetExposure"], "svd": v["svd_SetExposure"],
                    "shutmode": v["shutmode_SetExposure"]}
                for k, v in emu_result["errors"].items()
            },
            "speeds": {
                name: {
                    "tv_code": item["tv_code"],
                    "vts": item["vts"],
                    "period_q8": item["period_q8"],
                    "native": item["native"],
                    "electronic": item["electronic"],
                    "efcs_shd": item["efcs"]["shd"],
                }
                for name, item in emu_result["speeds"].items()
            },
            "cap73b": emu_result["cap73b"],
        },
        "cap73b_trace": {
            "description": "campo calculado por 0x43b1e520 antes del enganche C3-B; no se modifica",
            "instructions": trace_73b(originals.avcam),
            "writes": ["0x438acbfc (copia del plan)", "0x43b1e556", "0x43b1e55e"],
            "reads": ["0x438c8b4e", "0x43b1e448", "0x43b1e474", "0x43b1e7b6"],
            "source": "0x438acbfc copia cap+0x12e a plan+0x73b; 0x43b1e520 decide 0/1 con "
                      "0x73a, 0x655 y cap+0x12f8",
            "decision": "sin corrección verificada; C3-B no toca 0x73b (E25-28)",
        },
        "container": container,
        "independent_audit": independent_container_audit(),
        "limitations": [
            "No se ha instalado ni ejecutado en la cámara.",
            "El fin electrónico de integración y la ausencia de movimiento no están demostrados.",
            "La ruta larga (>= 1/15 s) queda fuera de C3-B.",
            "cap+0x73b conserva el valor nativo (E25-28).",
            "La recuperación de un Darwin que no arranque no está demostrada (E24-04).",
            "El guard del actualizador no se ha ejercitado con este contenedor.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
                   encoding="utf-8")

    manifest = build.binary_manifest(originals, built, rebuilt)
    for key in ("firmware_tar", "updater_img"):
        if key in manifest["inputs"] and "path" in manifest["inputs"][key]:
            manifest["inputs"][key]["path"] = str(
                Path(manifest["inputs"][key]["path"]).relative_to(ROOT)
            )
    (OUT.parent / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "all_ok": payload["emulation"]["all_ok"],
        "reversal": payload["reversal"]["verified"],
        "part_sum": payload["partition"]["part_sum_verified"],
        "changed_blocks": payload["partition"]["changed_blocks"],
        "container": bool(container),
    }, indent=2, ensure_ascii=False))
    if not payload["emulation"]["all_ok"] or not payload["reversal"]["verified"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
