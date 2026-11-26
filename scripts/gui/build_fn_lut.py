#!/usr/bin/env python3
"""Build reproducible de la opción «LUT» del menú Fn (G86 y G86-B): escribe SOLO ficheros (`lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so`, `share/app/string_*.uxc`);
no construye ni instala ningún CFW. Patrón de `build_cfw_objetivos.py` (los ajustes CFW van a la carpeta «CFW»; aquí además el nodo «LUT» como hijo de la raíz Fn).
FN-LUT-2: el cambio en tiempo real vive en `av-cam` (gancho de la máquina `0x437a24fc`, `lut_patch`); `avcam()` genera esa imagen parcheada (el CFW de objetivos la obtiene por `build_overlay_objetivos.AVCAM`).
Uso: build_fn_lut.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [--avcam AVCAM_ORIGINAL AVCAM_SALIDA]
G89/G116: 6 ranuras que la cámara lee de `LUT/LUT<n>.cube` (o del `.LUT` ya convertido) en la SD; las tablas NO viven en el `.dat`, así que sin tarjeta el ajuste queda en fábrica.
"""
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent), str(Path(__file__).resolve().parents[1] / "lut")]
import build_pp_menu
import cfw_ajustes
import lut_patch
import sd_lut


def main(dev_a, dev_b, dest) -> Path:
    """G116: la opción LUT tiene 6 ranuras que el userland (hilo en viewUnified2.so) rellena desde `X:/LUT/LUT<n>.cube` de la SD."""
    dest = Path(dest)
    cfw_ajustes.configurar_menu(sd_lut.ajustes_sd())
    build_pp_menu.FN_TREES[:] = ["lut"]
    build_pp_menu.SD_USERLAND = True
    try:
        build_pp_menu.main(dev_a, dev_b, dest)
    finally:
        build_pp_menu.FN_TREES.clear()
        build_pp_menu.SD_USERLAND = False
    return dest


def avcam(src, dest) -> Path:
    """`av-cam` con el ajuste «LUT» aplicado en caliente (cuevas en G18 + gancho de la máquina de estados); la tabla llega del Backup que escribe el userland (G89)."""
    dest = Path(dest)
    dest.write_bytes(lut_patch.apply_bytes(Path(src).read_bytes()))
    return dest


if __name__ == "__main__":
    a = sys.argv[1:]
    print(main(*a[:3]))
    if len(a) == 6 and a[3] == "--avcam":
        print(avcam(*a[4:6]))
