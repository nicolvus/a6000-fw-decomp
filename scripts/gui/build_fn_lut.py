#!/usr/bin/env python3
"""Build reproducible de la opción «LUT» del menú Fn (G86 y G86-B): escribe SOLO ficheros (`lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so`, `share/app/string_*.uxc`);
no construye ni instala ningún CFW. Patrón de `build_cfw_objetivos.py` (los ajustes CFW van a la carpeta «CFW»; aquí además el nodo «LUT» como hijo de la raíz Fn).
FN-LUT-2: el cambio en tiempo real vive en `av-cam` (gancho de la máquina `0x437a24fc`, `lut_patch`); `avcam()` genera esa imagen parcheada (el CFW de objetivos la obtiene por `build_overlay_objetivos.AVCAM`).
Uso: build_fn_lut.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [--avcam AVCAM_ORIGINAL AVCAM_SALIDA]
"""
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent), str(Path(__file__).resolve().parents[1] / "lut")]
import build_pp_menu
import cfw_ajustes
import lut_patch


def main(dev_a, dev_b, dest) -> Path:
    dest = Path(dest)
    cfw_ajustes.configurar_menu()
    build_pp_menu.FN_TREES[:] = ["lut"]
    try:
        build_pp_menu.main(dev_a, dev_b, dest)
    finally:
        build_pp_menu.FN_TREES.clear()
    return dest


def avcam(src, dest) -> Path:
    """`av-cam` con el ajuste «LUT» aplicado en caliente (cuevas de escritura + gancho de la máquina de estados)."""
    dest = Path(dest)
    dest.write_bytes(lut_patch.apply_bytes(Path(src).read_bytes()))
    return dest


if __name__ == "__main__":
    print(main(*sys.argv[1:4]))
    if len(sys.argv) == 7 and sys.argv[4] == "--avcam":
        print(avcam(*sys.argv[5:7]))
