#!/usr/bin/env python3
"""Build reproducible de la opción «LUT» del menú Fn (G86 y G86-B): escribe SOLO ficheros (`lib/CautionConfig.so`, `lib/viewUnified2.so`, `lib/viewUnified4.so`, `share/app/string_*.uxc`);
no construye ni instala ningún CFW. Patrón de `build_cfw_objetivos.py` (los ajustes CFW van a la carpeta «CFW»; aquí además el nodo «LUT» como hijo de la raíz Fn).
Uso: build_fn_lut.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA
"""
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent)]
import build_pp_menu
import cfw_ajustes


def main(dev_a, dev_b, dest) -> Path:
    dest = Path(dest)
    cfw_ajustes.configurar_menu()
    build_pp_menu.FN_TREES[:] = ["lut"]
    try:
        build_pp_menu.main(dev_a, dev_b, dest)
    finally:
        build_pp_menu.FN_TREES.clear()
    return dest


if __name__ == "__main__":
    print(main(*sys.argv[1:4]))
