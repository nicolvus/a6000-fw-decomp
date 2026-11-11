#!/usr/bin/env python3
"""G27 — CFW «completo»: Silent Shooting de tres estados (3.59) + menú Picture Profile completo + parches de RAM del núcleo. NO instala nada.

Encadena lo ya hecho, sin duplicar ninguna lógica:
  1. `build_silent_menu_test` (nodo Silent con ProcessId 0x12, página del menú, textos) + `silent_descriptor` (descriptor 0x12) → ficheros del 3.57+;
  2. `build_pp_menu` sobre esos ficheros (menú PP de 33 ajustes con Color Mode Level, gamma S-Log2/S-Log3/ITU709(800%), Color Mode B&W/S-Gamut/S-Gamut3(.Cine),
     Copy y Reset; `patch_libobj_pp`);
  3. eco de Silent en `libObj` (`g22.patch_libobj_eco`, 3.59) y, G30, eco del estado PP + selector de perfil (`patch_libobj_ppeco`, 3.67);
  4. `pp_curves_patch --color` sobre el BIONZ del CFW (3.38 + `g22.patch_tristate`): `pp_ram.sh` + `pp_curvas.bin` que `s_start_android.sh` lanza al arrancar
     (curvas de gamma, tablas y código de S-Gamut3/.Cine, escritos en la RAM del núcleo con comprobación previa de bytes);
  5. `build_nflasha15` (/usr con TPZL) y `build_package_nflasha15` (tar base del 3.57 con el BIONZ de tres estados, Darwin v3, sin `nflasha5`) → `.dat`.
Uso: build_cfw_completo.py SALIDA [--version 3.60]
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "scripts"))
import build_cfw_hooks as H
import build_nflasha15
import build_package_nflasha15
import build_pp_menu
import patch_libobj_ppeco
import build_silent_menu_test
import pp_curves_patch
from g22 import patch_libobj_eco, patch_tristate

DEV_A = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
DEV_B = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
BASE_TAR = ROOT / "analysis/gui/g22/base-357.tar"
USR = "nflasha15_unpacked_unpacked"
PID_SILENT, SILENT_DELTA = 0x12, 0xEB0     # nodo de Silent = RootAelWShutter + 0xEB0 (build_silent_menu_test)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def md5(b: bytes) -> str:
    return hashlib.md5(b, usedforsecurity=False).hexdigest()


def eco(libobj: bytes) -> bytes:
    out = bytearray(libobj)
    for a, old, new, _ in patch_libobj_eco.SITES:
        assert libobj[a:a + len(old)] == old, hex(a)
        out[a:a + len(new)] = new
    return bytes(out)


def build_files(work: Path) -> Path:
    """Paquete de ficheros de /usr (MANIFEST.json incluido) en work/files."""
    orig = DEV_A / USR
    silent = work / "silent"
    build_silent_menu_test.main(DEV_A, DEV_B, silent, pid_silent=PID_SILENT)
    stage = work / "stage"
    for rel in ("lib/libObj.so", "lib/CautionConfig.so", "lib/viewUnified2.so"):
        (stage / USR / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(orig / rel, stage / USR / rel)
    (stage / USR / "share/app").mkdir(parents=True, exist_ok=True)
    for f in (orig / "share/app").glob("string_*.uxc"):
        shutil.copy(f, stage / USR / "share/app" / f.name)
    shutil.copy(silent / "lib/CautionConfig.so", stage / USR / "lib/CautionConfig.so")   # con el nodo Silent; viewUnified2 se parchea una sola vez (add_menu_entry no es reentrante)
    for f in (silent / "share/app").glob("*.uxc"):
        shutil.copy(f, stage / USR / "share/app" / f.name)
    pp = work / "pp"
    build_pp_menu.main(stage, DEV_B, pp, entradas_previas=[SILENT_DELTA], silent=True, **build_pp_menu.configurar(gam=True, col=True, acc=True))

    files = work / "files"
    for rel in json.loads((pp / "MANIFEST.json").read_text())["parcheados"]:
        (files / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(pp / rel, files / rel)
    (files / "lib/libObj.so").write_bytes(patch_libobj_ppeco.patch(eco((pp / "lib/libObj.so").read_bytes())))   # G30: eco del estado PP y selector de perfil (nuevo LOAD al final)
    # núcleo: BIONZ del CFW (3.38 + tres estados) → pp_ram.sh + pp_curvas.bin
    bionz, _ = patch_tristate.apply_bytes((ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin").read_bytes())
    (work / "av-cam.cfw.bin").write_bytes(bionz)
    pp_curves_patch.main(work / "av-cam.cfw.bin", work / "ram", None, color=True)
    (files / "bin").mkdir(exist_ok=True)
    shutil.copy(work / "ram/pp_ram.sh", files / "bin/pp_ram.sh")
    shutil.copy(work / "ram/pp_curvas.bin", files / "bin/pp_curvas.bin")
    start = (orig / "bin/s_start_android.sh").read_text()
    (files / "bin/s_start_android.sh").write_text(H.con_gancho_ram(start))

    nuevos = {"bin/pp_ram.sh": "755", "bin/pp_curvas.bin": "644"}
    parcheados = sorted(set(json.loads((pp / "MANIFEST.json").read_text())["parcheados"]) | {"bin/s_start_android.sh"})
    man = {"idiomas": json.loads((pp / "MANIFEST.json").read_text())["idiomas"], "nuevos": nuevos, "originales": {}, "parcheados": {}, "md5": {}}
    for rel in parcheados:
        o, n = (orig / rel).read_bytes(), (files / rel).read_bytes()
        man["originales"][rel], man["parcheados"][rel] = sha(o), sha(n)
        man["md5"][rel] = {"original": md5(o), "parcheado": md5(n)}
    (files / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))
    (files / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in man["parcheados"].items()))
    return files


def main(out: Path, version: str) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    files = build_files(out)
    nf15 = out / f"nflasha15-{version.replace('.', '')}.bin"
    rep15 = build_nflasha15.main(DEV_A / "nflasha15", files, nf15)
    pkg = out / f"pkg-{version}"
    res = build_package_nflasha15.main(nf15, pkg, BASE_TAR, version, darwin_v3=True, sin_wbi=True)
    (out / "build-nflasha15.json").write_text(json.dumps(rep15, indent=1))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("salida", type=Path)
    ap.add_argument("--version", default="3.60")
    a = ap.parse_args()
    print(json.dumps(main(a.salida, a.version), indent=1))
