#!/usr/bin/env python3
"""E2E-2 (G75 T47) — overlay local con TODOS los parches sueltos de las funciones objetivo, para cargarlo en el arnés (`live.py --pkg OVERLAY --avcam-de OVERLAY.nflasha3`). NO instala nada.

Sin lógica propia: encadena los generadores existentes sobre los binarios de Sony 3.21 (nflasha15 `/usr`) y sobre el av-cam del CFW (`build_base_pp`, nflasha3):
  - menú: `cfw_ajustes.construir` (carpeta «CFW», 13 ajustes) → `viewUnified2.so`, `CautionConfig.so`, `string_*.uxc`;
  - `CautionConfig.so` además: Extra Fine (G39), lista ISO 51200 (G43), HD120 (G70);
  - `libObj.so`: ISO MAX 102400 (G42), XAVC S sin restricción de tarjeta (G79), Intervalo (G61), DR Prioridad (G68), Zebra Nivel (G84), S&Q (G76);
  - `av-cam` (junto al overlay, `OVERLAY.nflasha3`): CFW base (curvas PP, tres estados) + Flicker Scan (sustituye el Silent r5 estándar: lo incluye, G63), Bulb Timer (G55),
    Color Chrome (G69), LUT 3D (G71), S&Q 120/100 (G76), contador de Live ND (G65).
Quedan fuera (no tienen parche o no hay gancho): Focus Bracket (gancho sin localizar), HLG (menú PP), Keystone.
Uso: build_overlay_objetivos.py DESTINO   (crea DESTINO/cam/usr/… y DESTINO.nflasha3)
"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for d in ("scripts", "scripts/gui", "scripts/g55", "scripts/g61", "scripts/g63", "scripts/g65", "scripts/g68", "scripts/g69", "scripts/g76", "scripts/g84", "scripts/lut", "references/pmca"):
    sys.path.insert(0, str(ROOT / d))
import bulb_timer_patch
import build_base_pp
import cfw_ajustes
import color_chrome_patch
import drp_patch
import flicker_scan_patch
import hd120_list_patch
import intervalo_patch
import iso_list_patch
import iso_max_patch
import jpeg_hook_patch
import lut_patch
import quality_exfine_patch
import sq120_patch
import sq_libobj_patch
import xavcs_card_patch
import zebra_patch
from e25_27 import build, tarball

DEV_A = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
DEV_B = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
BASE_TAR = ROOT / "analysis/gui/g22/base-380.tar"
USR = DEV_A / "nflasha15_unpacked_unpacked"
CAUTION = (quality_exfine_patch.patch, iso_list_patch.patch, hd120_list_patch.patch)
LIBOBJ = (iso_max_patch.patch, xavcs_card_patch.patch, intervalo_patch.apply_bytes, drp_patch.apply_bytes, zebra_patch.apply_bytes, sq_libobj_patch.apply_bytes)
AVCAM = (flicker_scan_patch.apply_bytes, bulb_timer_patch.apply_bytes, color_chrome_patch.apply_bytes, lut_patch.apply_bytes, sq120_patch.patch, jpeg_hook_patch.apply_bytes)


def encadena(d: bytes, parches) -> bytes:
    for p in parches:
        d = p(d)
    return d


def main(dest: Path) -> dict:
    dest = Path(dest)
    usr = dest / "cam/usr"
    with tempfile.TemporaryDirectory() as t:
        cfw_ajustes.construir(DEV_A, DEV_B, t)
        menu = Path(t)
        ficheros = {f.relative_to(menu).as_posix(): f.read_bytes() for f in menu.rglob("*") if f.is_file() and f.name != "MANIFEST.json"}
        ficheros["lib/CautionConfig.so"] = encadena(ficheros["lib/CautionConfig.so"], CAUTION)
        ficheros["lib/libObj.so"] = encadena((USR / "lib/libObj.so").read_bytes(), LIBOBJ)
        for rel, b in ficheros.items():
            (usr / rel).parent.mkdir(parents=True, exist_ok=True)
            (usr / rel).write_bytes(b)
        tar = Path(t) / "base.tar"
        info = build_base_pp.main(BASE_TAR, tar, silent_r5=False, post=lambda av: encadena(av, AVCAM))
        miembros = {e.name: e.data for e in tarball.parse(tar.read_bytes())[0]}
        Path(str(dest) + ".nflasha3").write_bytes(miembros[build.NFLASHA3])
    man = {rel: hashlib.sha256(b).hexdigest() for rel, b in sorted(ficheros.items())}
    (usr / "MANIFEST.json").write_text(json.dumps({"parcheados": man, "avcam": info}, indent=1))
    return {"ficheros": len(man), "avcam": info}


if __name__ == "__main__":
    print(json.dumps(main(Path(sys.argv[1])), indent=1))
