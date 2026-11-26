#!/usr/bin/env python3
"""Dry-run de `scripts/gui/build_package_nflasha15.py` CONSERVANDO `dev/nflasha5` (WBI de Sony).

Reproduce en memoria los mismos pasos que `build_package_nflasha15.main(..., sin_wbi=False)`
hasta el punto en que escribiría `firmware.tar` + `firmware_packed.dat`, y NO los escribe.
Comprueba que:
  * la base (`build/cfw_func393/base/base-film.tar`) ya trae `0700_part_image/dev/nflasha5`
    byte a byte igual al de Sony 3.21 y su línea en `part_image.sum`;
  * `sin_wbi=False` deja las dos cosas intactas y solo cambia `dev/nflasha15` + su suma;
  * `sin_wbi=True` (lo que hizo el 3.93 instalado) quita el miembro y la línea.

Uso: .venv/bin/python3 reports/evidence/film-pb-1-sub-arranque-wbi-20261128/dry-run-wbi.py
No toca la cámara ni escribe ningún artefacto de firmware.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/gui"))

import build_package_nflasha15 as BP  # noqa: E402
from e25_27 import build, sums, tarball  # noqa: E402

BASE_TAR = ROOT / "build/cfw_func393/base/base-film.tar"
NFLASHA15_BIN = ROOT / "build/cfw_func393/base/nflasha15-393.bin"
SONY_WBI = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5"
WBI_SHA = "fe080cda9f330537f36d7e9e283ecd69e4e8096d974dbdd16d598a8cbdcf3f04"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> dict:
    base = BASE_TAR.read_bytes()
    entries, _ = tarball.parse(base)
    members = {e.name: e.data for e in entries}
    blob = NFLASHA15_BIN.read_bytes()

    checks: list[dict] = []

    def chk(name: str, ok: bool, detalle: str = "") -> None:
        checks.append({"comprobacion": name, "ok": bool(ok), "detalle": detalle})
        assert ok, name

    # --- estado de partida -------------------------------------------------
    chk("base_tar contiene 0700_part_image/dev/nflasha5", BP.NFLASHA5 in members,
        f"{len(members[BP.NFLASHA5])} B" if BP.NFLASHA5 in members else "AUSENTE")
    chk("nflasha5 de la base == nflasha5 de Sony 3.21 (sha256)", sha(members[BP.NFLASHA5]) == WBI_SHA, WBI_SHA)
    chk("nflasha5 de la base == dev/nflasha5 desempaquetado del fw321",
        sha(members[BP.NFLASHA5]) == sha(SONY_WBI.read_bytes()))
    chk("base_tar contiene 0700_part_image/dev/nflasha15", BP.NFLASHA15 in members,
        f"{len(members[BP.NFLASHA15])} B")
    chk("nflasha15 nuevo existe y difiere del de la base", NFLASHA15_BIN.is_file(),
        f"{len(blob)} B, sha256 {sha(blob)[:16]}…")

    base_sum = members[build.PART_SUM].decode("ascii")
    lineas_wbi = [ln for ln in base_sum.splitlines() if ln.rstrip().endswith(",dev/nflasha5,")]
    chk("part_image.sum de la base tiene exactamente 1 línea de dev/nflasha5", len(lineas_wbi) == 1,
        lineas_wbi[0] if lineas_wbi else "AUSENTE")
    chk("esa línea verifica contra los bytes del miembro",
        sums.verify(base_sum, "dev/nflasha5", members[BP.NFLASHA5]))

    # --- lo que hace main() con sin_wbi=False ------------------------------
    part_sum, detail = sums.update(base_sum, BP.ENTRY, blob)
    chk("sums.update reescribe solo dev/nflasha15", sums.verify(part_sum, BP.ENTRY, blob),
        detail["line_after"])
    chk("sin_wbi=False conserva la línea de dev/nflasha5",
        sum(1 for ln in part_sum.splitlines() if ln.rstrip().endswith(",dev/nflasha5,")) == 1)

    repl: dict[str, bytes | None] = {BP.NFLASHA15: blob, build.PART_SUM: part_sum.encode("ascii")}
    chk("sin_wbi=False -> NO se pone nflasha5 a None en repl", BP.NFLASHA5 not in repl)
    tar_wbi, info_wbi = tarball.rebuild(base, repl)
    out_wbi = {e.name: e.data for e in tarball.parse(tar_wbi)[0]}
    chk("tar con WBI: miembro nflasha5 idéntico byte a byte", out_wbi[BP.NFLASHA5] == members[BP.NFLASHA5])
    chk("tar con WBI: nflasha15 nuevo", out_wbi[BP.NFLASHA15] == blob)
    chk("tar con WBI: suma de nflasha5 sigue verificando",
        sums.verify(out_wbi[build.PART_SUM].decode("ascii"), "dev/nflasha5", out_wbi[BP.NFLASHA5]))
    chk("tar con WBI: suma de nflasha15 verifica",
        sums.verify(out_wbi[build.PART_SUM].decode("ascii"), BP.ENTRY, out_wbi[BP.NFLASHA15]))
    cambiados = sorted(i["name"] for i in info_wbi)
    chk("tar con WBI: solo 2 miembros reescritos", cambiados == sorted([BP.NFLASHA15, build.PART_SUM]),
        ", ".join(cambiados))
    chk("tar con WBI: mismos 105 miembros que la base", len(out_wbi) == len(members), str(len(out_wbi)))

    # --- contraste: sin_wbi=True (lo que se instaló como 3.93) -------------
    lines = base_sum.splitlines(keepends=True)
    sum_sin = "".join(ln for ln in lines if not ln.rstrip().endswith(",dev/nflasha5,"))
    repl_sin: dict[str, bytes | None] = {BP.NFLASHA15: blob, build.PART_SUM: sum_sin.encode("ascii"), BP.NFLASHA5: None}
    tar_sin, _ = tarball.rebuild(base, repl_sin)
    out_sin = {e.name: e.data for e in tarball.parse(tar_sin)[0]}
    chk("sin_wbi=True: el miembro nflasha5 desaparece", BP.NFLASHA5 not in out_sin)
    chk("sin_wbi=True: la línea del sum desaparece",
        not any(ln.rstrip().endswith(",dev/nflasha5,") for ln in out_sin[build.PART_SUM].decode("ascii").splitlines()))

    # --- darwin v3 (el 3.93 lo lleva) -------------------------------------
    core, _ = build.efcs_tabla_diff(members[build.DARWIN_CORE])
    dsum, _ = build._sum_text_with_core(members[build.DARWIN_SUM].decode("ascii"), core)
    chk("--darwin-v3 aplicable sobre esta base (darwin_core distinto)", core != members[build.DARWIN_CORE],
        f"sha256 {sha(core)[:16]}…")
    chk("--darwin-v3: la suma de darwin verifica", dsum and len(dsum) > 0)

    return {
        "modo": "DRY RUN — no se escribió firmware.tar ni firmware_packed.dat",
        "base_tar": str(BASE_TAR.relative_to(ROOT)),
        "nflasha15_nuevo": str(NFLASHA15_BIN.relative_to(ROOT)),
        "version_propuesta": "3.94 (debe ser > 3.93 instalada)",
        "miembros_base": len(members),
        "miembros_con_wbi": len(out_wbi),
        "tar_con_wbi_sha256": sha(tar_wbi),
        "tar_con_wbi_bytes": len(tar_wbi),
        "nflasha5_sha256": sha(out_wbi[BP.NFLASHA5]),
        "comprobaciones": checks,
        "todo_ok": all(c["ok"] for c in checks),
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=1, ensure_ascii=False))
