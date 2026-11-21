"""G88 — LUTs propios desde ficheros `.cube` (cualquier tamaño: 17/32/33/64…): convierte a las 3 tablas del ISP (5×9×9) y pone sus nombres en la opción «LUT».
Ruta PC (la cámara NO lee la SD: g88 §1). Uso: `sd_lut.py CARPETA_CUBE [--medir]` imprime nombres y ΔE; `build_fn_lut.py --cubes CARPETA` los integra en el build.
"""
import dataclasses
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).parent)]
import cfw_ajustes
import cube_a6000 as C

MAX_LUTS = 3          # la cueva de g73 tiene 3 tablas de 21 bits (zona B de 3432 B); más exige otra zona verificada
MAX_NOMBRE = 11       # prudencia: los nombres de fábrica miden ≤ 11 («Teal&Orange»); no medido el tope de la franja Fn


def lee_cubes(carpeta: Path) -> list[tuple[str, np.ndarray, np.ndarray, np.ndarray]]:
    """(nombre, tabla, dom_min, dom_max) de los `*.cube` de la carpeta, por orden alfabético, máx. `MAX_LUTS`."""
    ficheros = sorted(Path(carpeta).glob("*.cube"), key=lambda p: p.name.lower())
    if not ficheros:
        raise ValueError(f"sin ficheros .cube en {carpeta}")
    if len(ficheros) > MAX_LUTS:
        raise ValueError(f"{len(ficheros)} .cube: máximo {MAX_LUTS}")
    out = []
    for p in ficheros:
        tab, lo, hi = C.lee_cube(p)
        out.append((p.stem[:MAX_NOMBRE], tab, lo, hi))
    return out


def convierte(cubes, img: bytes | None = None) -> tuple[list[bytes], list[str], list[tuple[float, float]]]:
    """→ (3 tablas de 0x654 B, 3 nombres, ΔE2000 (medio, p95) del .cube exacto frente a lo que aplica el ISP). Faltantes = identidad «Neutro»."""
    img = img if img is not None else C.BIN.read_bytes()
    x = np.random.default_rng(7).random((20000, 3))
    tablas, nombres, de = [], [], []
    for nombre, tab, lo, hi in cubes:
        f = lambda v, tab=tab, lo=lo, hi=hi: C.aplica_cube(tab, lo, hi, v)
        ch = C.descompone(f, False, False, True)
        tablas.append(C.empaqueta_hw(ch.q, img))
        nombres.append(nombre)
        e = C.de2000(f(x), ch(x))
        de.append((float(e.mean()), float(np.percentile(e, 95))))
    ident = C.empaqueta_hw(C.descompone(C.SINT["identidad"], False, False, True).q, img)
    while len(tablas) < MAX_LUTS:
        tablas.append(ident)
        nombres.append("Neutro")
        de.append((0.0, 0.0))
    return tablas, nombres, de


def ajustes_con_nombres(nombres: list[str]) -> tuple:
    """`cfw_ajustes.AJUSTES` con las opciones del ajuste «LUT» = Off + `nombres` (valores 0…3); se pasa a `configurar_menu(ajustes)`."""
    aj = dataclasses.replace(cfw_ajustes.POR_ID["lut"], opciones=(("Off", 0),) + tuple((n, i + 1) for i, n in enumerate(nombres)))
    return tuple(aj if a.id == "lut" else a for a in cfw_ajustes.AJUSTES)


if __name__ == "__main__":
    tabs, nom, de = convierte(lee_cubes(Path(sys.argv[1])))
    for n, (m, p) in zip(nom, de):
        print(f"{n:12s} ΔE2000 medio {m:.2f} p95 {p:.2f}")


def ajustes_sd() -> tuple:
    """G89: `AJUSTES` con «LUT» = Off + 6 ranuras (`LUT 1…6`): el contenido sale de `X:/LUT/LUT<n>.cube` en la SD (userland), no del `.dat`."""
    import lut_patch
    return tuple(lut_patch.AJ_SD if a.id == "lut" else a for a in cfw_ajustes.AJUSTES)
