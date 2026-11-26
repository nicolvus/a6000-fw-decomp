#!/usr/bin/env python3
"""FILM-PB-1 sub — verificación offline de los tres flasheos candidatos (26-11-2026).

Solo lectura: hashea y parsea artefactos ya presentes en el repo. No abre la cámara, no
ejecuta pmca, no construye ningún DAT ni escribe fuera de este directorio.

Uso: .venv/bin/python3 reports/evidence/film-pb-1-sub-riesgo-flash-20261126/verificar-riesgo-flash.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tarball, tpzl  # noqa: E402


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def esc(path: Path) -> dict:
    return {"ruta": str(path.relative_to(ROOT)), "existe": path.exists(),
            "bytes": path.stat().st_size if path.exists() else None,
            "sha256": sha(path.read_bytes()) if path.exists() and path.stat().st_size < 300_000_000 else None}


def tar_facts(path: Path) -> dict:
    raw = path.read_bytes()
    members = {e.name: e.data for e in tarball.parse(raw)[0]}
    dev = {k.split("/")[-1]: v for k, v in members.items() if k.startswith("0700_part_image/dev/")}
    sums = {k: members[k].decode("ascii", "replace") for k in members if k.endswith(".sum")}
    out = {
        "tar_sha256": sha(raw), "miembros": len(members),
        "particiones_en_tar": {k: {"bytes": len(v), "sha256": sha(v)} for k, v in sorted(dev.items())},
        "sumas_presentes": sorted(sums),
        "updater_sum_o_loader_sum": any(k.endswith(("updater.sum", "loader.sum")) for k in sums),
        "part_image_sum": sums.get("0701_part_image_sum/part_image.sum", "").splitlines(),
        "nflasha3_hardware_violations": None,
    }
    if "nflasha3" in dev:
        img = tpzl.TpzlImage.parse(dev["nflasha3"])
        out["nflasha3_hardware_violations"] = tpzl.hardware_violations(img)
        out["nflasha3_bloques"] = len(img.entries)
    if "0640_darwin/darwin_core.bin" in members:
        out["darwin_sha256"] = sha(members["0640_darwin/darwin_core.bin"])
    return out


def libmpr_sony(sony_dir: Path) -> dict:
    """libmpr.so de fábrica: vive dentro del ext2 de nflasha15 ya extraído (raíz = /usr)."""
    for cand in [sony_dir / "nflasha15_unpacked_unpacked/lib/libmpr.so",
                 ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
                        "nflasha15_unpacked_unpacked/lib/libmpr.so"]:
        if cand.exists():
            a = cand.read_bytes()
            b = (ROOT / "build/cfw_bypass_guardas/libmpr.so").read_bytes()
            return {"ruta": str(cand.relative_to(ROOT)), "sha256": sha(a), "bytes": len(a),
                    "diff_bytes": sum(1 for x, y in zip(a, b) if x != y)}
    return {"ruta": None, "existe": False}


def main() -> dict:
    sony_dir = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
    resultado = {
        "A_dat_oficial_321": esc(ROOT / "firmware/extracted/updater/Update_ILCE6000V321/Resources/"
                                      "FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat"),
        "A_dat_404_equivalente": esc(ROOT / "build/sony_puro_sin_wbi_404/package-4.04/firmware_packed.dat"),
        "C_libmpr_parcheado": esc(ROOT / "build/cfw_bypass_guardas/libmpr.so"),
        "C_libmpr_sony": libmpr_sony(sony_dir),
        "B_tars_base": {p: tar_facts(ROOT / p) for p in [
            "firmware/extracted/fw321/firmware.tar",
            "analysis/e25-27/artifacts-338/firmware.integrated.tar",
            "analysis/gui/g22/base-380.tar",
            "build/cfw_func393/base/base-film.tar",
        ]},
        "nflasha5_identico_a_sony": {},
    }
    sony5 = (sony_dir / "nflasha5").read_bytes()
    for name, base in resultado["B_tars_base"].items():
        resultado["nflasha5_identico_a_sony"][name] = (
            base["particiones_en_tar"]["nflasha5"]["sha256"] == sha(sony5))
    return resultado


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, ensure_ascii=False))
