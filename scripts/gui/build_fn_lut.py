#!/usr/bin/env python3
"""Build reproducible de la opción «LUT» del menú Fn (G86): escribe SOLO ficheros (`lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so`, `share/app/string_*.uxc`);
no construye ni instala ningún CFW. Patrón de `build_cfw_objetivos.py` (los ajustes CFW van a la carpeta «CFW»; aquí además el nodo «LUT» como hijo de la raíz Fn).
Uso: build_fn_lut.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent)]
import build_pp_menu
import cfw_ajustes
import fn_lut_menu


def main(dev_a, dev_b, dest) -> Path:
    dest = Path(dest)
    cfw_ajustes.configurar_menu()
    build_pp_menu.FN_TREES[:] = ["lut"]
    try:
        build_pp_menu.main(dev_a, dev_b, dest)
    finally:
        build_pp_menu.FN_TREES.clear()
    a = Path(dev_a) / "nflasha15_unpacked_unpacked"
    delta = fn_lut_menu.delta_respecto_memoryrecall((a / "lib/CautionConfig.so").read_bytes(), build_pp_menu.FN_DELTAS[0])
    vu4 = fn_lut_menu.patch_vu4((a / "lib/viewUnified4.so").read_bytes(), delta)
    (dest / "lib/viewUnified4.so").write_bytes(vu4)
    man = json.loads((dest / "MANIFEST.json").read_text())
    man["originales"]["lib/viewUnified4.so"] = hashlib.sha256((a / "lib/viewUnified4.so").read_bytes()).hexdigest()
    man["parcheados"]["lib/viewUnified4.so"] = hashlib.sha256(vu4).hexdigest()
    (dest / "MANIFEST.json").write_text(json.dumps(man, indent=1, sort_keys=True))
    (dest / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in man["parcheados"].items()))
    return dest


if __name__ == "__main__":
    print(main(*sys.argv[1:4]))
