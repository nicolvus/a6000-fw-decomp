#!/usr/bin/env python3
"""G97 — CFW «Film»: SOLO Silent Shooting (tres estados del 3.80 + Silent calibrado R87) y el menú «Film» con los 38 looks de G97. Nada más del CFW:
sin Picture Profile, sin LUT de la SD, sin el resto de ajustes. NO instala nada.

Encadena lo existente:
  1. `build_silent_menu_test` (nodo Silent pid 0x12, página, textos) y `silent_descriptor`;
  2. `build_pp_menu` con la especificación sustituida por la carpeta «Film» (8 filas de ≤ 7 opciones, ajustes CFW de 1 B) + el userland de
     `film_userland` en `viewUnified2.so` (`DT_INIT` → `films_hilo`, datos de los 38 looks en el mismo segmento);
  3. `libObj.so` = 3.21 + eco de Silent (`patch_libobj_eco`), sin el parche PP;
  4. BIONZ = el de `base-380.tar` (3.38 + tres estados con Silent manda sobre EFCS) + `patch_silent_r5` (R87) + `film_patch` (LUT + curva tras la gamma);
  5. `build_nflasha15` + `build_package_nflasha15` (Darwin v3, sin `nflasha5`).
Uso: build_cfw_film.py SALIDA [--version 3.87] [--looks analysis/lut/g97/looks.npz]
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("scripts/gui", "scripts", "scripts/lut", "scripts/g22"):
    sys.path.insert(0, str(ROOT / d))
import build_base_pp
import build_cfw_completo as C
import build_nflasha15
import build_package_nflasha15
import build_pp_menu
import build_silent_menu_test
import film_patch
import film_userland as FU
import patch_silent_r5
import pp_menu_spec as M

LOOKS = ROOT / "analysis/lut/g97/looks.npz"


def bionz(original: bytes) -> bytes:
    """3.38 + tres estados (base-380) → + Silent calibrado (R87) → + películas."""
    return film_patch.apply_bytes(patch_silent_r5.apply_bytes(original))


def menu_film() -> None:
    """La especificación del menú pasa a ser solo la carpeta «Film» (los ajustes guardan 1 B en el Backup; sin Picture Profile)."""
    aj = FU.ajustes()
    M.SETTINGS.clear()
    for a in aj:
        M.SETTINGS[a.id] = M.S(a.id, a.label, 0, tuple((t, i) for i, (t, _) in enumerate(a.opciones)), "g97", backup=a.backup)
    M.TREE = ("folder", FU.CARPETA, M.paginar([a.id for a in aj]))
    M.PIDS[:] = range(M.PIDS[0], M.PIDS[0] + len(aj))
    build_pp_menu.EXTRA_TREES[:] = []
    build_pp_menu.FN_TREES[:] = []
    build_pp_menu.SD_USERLAND = False


def build_files(work: Path, looks: Path) -> Path:
    orig = C.DEV_A / C.USR
    silent = work / "silent"
    build_silent_menu_test.main(C.DEV_A, C.DEV_B, silent, pid_silent=C.PID_SILENT)
    stage = work / "stage"
    for rel in ("lib/libObj.so", "lib/CautionConfig.so", "lib/viewUnified2.so", "lib/viewUnified4.so"):
        (stage / C.USR / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(orig / rel, stage / C.USR / rel)
    (stage / C.USR / "share/app").mkdir(parents=True, exist_ok=True)
    for f in (orig / "share/app").glob("string_*.uxc"):
        shutil.copy(f, stage / C.USR / "share/app" / f.name)
    shutil.copy(silent / "lib/CautionConfig.so", stage / C.USR / "lib/CautionConfig.so")
    for f in (silent / "share/app").glob("*.uxc"):
        shutil.copy(f, stage / C.USR / "share/app" / f.name)
    menu_film()
    pp = work / "pp"
    build_pp_menu.main(stage, C.DEV_B, pp, entradas_previas=[C.SILENT_DELTA], silent=True)
    files = work / "files"
    parcheados = sorted(json.loads((pp / "MANIFEST.json").read_text())["parcheados"]) + ["lib/libObj.so"]
    for rel in parcheados:
        (files / rel).parent.mkdir(parents=True, exist_ok=True)
        if rel != "lib/libObj.so":
            shutil.copy(pp / rel, files / rel)
    (files / "lib/libObj.so").write_bytes(C.eco((orig / "lib/libObj.so").read_bytes()))
    (files / "lib/viewUnified2.so").write_bytes(FU.patch_vu2((files / "lib/viewUnified2.so").read_bytes(), FU.compila(looks)))
    man = {"idiomas": json.loads((pp / "MANIFEST.json").read_text())["idiomas"], "nuevos": {}, "originales": {}, "parcheados": {}, "md5": {}}
    for rel in sorted(set(parcheados)):
        o, n = (orig / rel).read_bytes(), (files / rel).read_bytes()
        man["originales"][rel], man["parcheados"][rel] = C.sha(o), C.sha(n)
        man["md5"][rel] = {"original": C.md5(o), "parcheado": C.md5(n)}
    (files / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))
    (files / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in man["parcheados"].items()))
    return files


def main(out: Path, version: str, looks: Path = LOOKS) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    files = build_files(out, looks)
    nf15 = out / f"nflasha15-{version.replace('.', '')}.bin"
    rep15 = build_nflasha15.main(C.DEV_A / "nflasha15", files, nf15)
    base = out / "base-film.tar"
    rep_base = build_base_pp.main(C.BASE_TAR, base, bionz=bionz)
    res = build_package_nflasha15.main(nf15, out / f"pkg-{version}", base, version, darwin_v3=True, sin_wbi=True)
    (out / "build-nflasha15.json").write_text(json.dumps(rep15, indent=1))
    (out / "build-base.json").write_text(json.dumps(rep_base, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("salida", type=Path)
    ap.add_argument("--version", default="3.87")
    ap.add_argument("--looks", type=Path, default=LOOKS)
    a = ap.parse_args()
    print(json.dumps(main(a.salida, a.version, a.looks), indent=1))
