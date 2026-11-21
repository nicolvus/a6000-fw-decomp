#!/usr/bin/env python3
"""Build reproducible de la opción «LUT» del menú Fn (G86 y G86-B): escribe SOLO ficheros (`lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so`, `share/app/string_*.uxc`);
no construye ni instala ningún CFW. Patrón de `build_cfw_objetivos.py` (los ajustes CFW van a la carpeta «CFW»; aquí además el nodo «LUT» como hijo de la raíz Fn).
FN-LUT-2: el cambio en tiempo real vive en `av-cam` (gancho de la máquina `0x437a24fc`, `lut_patch`); `avcam()` genera esa imagen parcheada (el CFW de objetivos la obtiene por `build_overlay_objetivos.AVCAM`).
Uso: build_fn_lut.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [--cubes CARPETA | --sd] [--avcam AVCAM_ORIGINAL AVCAM_SALIDA]
`--sd` (G89, LUT-SD-1): 6 ranuras que la cámara lee de `LUT/LUT<n>.cube` en la SD (hilo del userland en viewUnified2.so + lectura del Backup en av-cam).
`--cubes`: LUTs propios (G88): los `.cube` de la carpeta (≤3, cualquier tamaño) dan nombre y tabla a los looks 1…3.
"""
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent), str(Path(__file__).resolve().parents[1] / "lut")]
import build_pp_menu
import cfw_ajustes
import lut_patch
import sd_lut


def main(dev_a, dev_b, dest, ajustes=cfw_ajustes.AJUSTES, sd=False) -> Path:
    """`sd`: G89, la opción LUT tiene 6 ranuras que el userland (hilo en viewUnified2.so) rellena desde `X:/LUT/LUT<n>.cube` de la SD."""
    dest = Path(dest)
    if sd:
        ajustes = sd_lut.ajustes_sd()
    cfw_ajustes.configurar_menu(ajustes)
    build_pp_menu.FN_TREES[:] = ["lut"]
    build_pp_menu.SD_USERLAND = sd
    try:
        build_pp_menu.main(dev_a, dev_b, dest)
    finally:
        build_pp_menu.FN_TREES.clear()
        build_pp_menu.SD_USERLAND = False
    return dest


def avcam(src, dest, tablas=None, sd=False) -> Path:
    """`av-cam` con el ajuste «LUT» aplicado en caliente (cuevas de escritura + gancho de la máquina de estados); `sd`: tablas desde el Backup que escribe el userland (G89)."""
    dest = Path(dest)
    dest.write_bytes(lut_patch.apply_bytes(Path(src).read_bytes(), tablas, sd))
    return dest


if __name__ == "__main__":
    a = sys.argv[1:]
    tablas = ajustes = None
    if "--cubes" in a:
        k = a.index("--cubes")
        tablas, nombres, _ = sd_lut.convierte(sd_lut.lee_cubes(Path(a[k + 1])))
        ajustes = sd_lut.ajustes_con_nombres(nombres)
        del a[k:k + 2]
    sd = "--sd" in a
    if sd:
        a.remove("--sd")
    print(main(*a[:3], *([ajustes] if ajustes else [cfw_ajustes.AJUSTES]), sd))
    if len(a) == 6 and a[3] == "--avcam":
        print(avcam(*a[4:6], tablas, sd))
