#!/usr/bin/env python3
"""LUTs de film simulation ajustadas a la LUT 3D de la A6000 (5×9×9, ΔY ±25 %, ΔC ±18 %) para la SD (G89).

Los `.cube` de partida (Fujifilm, entrada Apple Log) sobre la señal de pantalla de la A6000 actúan como una curva dura (ganancia de ruido ×1,8–2,4, g91):
primero se hornea la entrada (sRGB → lineal → Rec.2020 → Apple Log), luego se ajusta la tabla del hardware en ΔE2000 (lut_opt.py) y por último se escribe un
`.cube` 33³ que `lutsd.c` (muestreo directo + corrección G90) convierte en esa misma tabla; la diferencia de la corrección se pre-compensa por iteración.

uso: film_a6000.py CARPETA_FILMS SALIDA [nombre ...]   → SALIDA/<nombre>.cube + informe.json
shortcut: la entrada de la cámara se supone sRGB (no medida) y los pesos son sintéticos (neutros/piel); cambiar `entrada()` si se mide otra EOTF.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import cube_a6000 as C
import lut_opt as O
import lut_sd_userland as U

NOMBRES = ["ACROS", "ASTIA", "ETERNA", "PROVIA", "Velvia", "REALA-ACE"]
R0, RT, CA, BETA, GAM, DELTA = -0.05641088, 0.01, 47.28711236, 0.00964052, 0.08550479, 0.69336945
M709_2020 = np.array([[0.6274, 0.3293, 0.0433], [0.0691, 0.9195, 0.0114], [0.0164, 0.0880, 0.8956]])


def entrada(x: np.ndarray) -> np.ndarray:
    """RGB de pantalla (sRGB) → Apple Log (Rec.2020), la entrada para la que están hechos los `.cube`."""
    lin = np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4) @ M709_2020.T
    return np.clip(np.where(lin >= RT, GAM * np.log2(np.maximum(lin, RT) + BETA) + DELTA, CA * (lin - R0) ** 2), 0, 1)


def objetivo(ruta: Path):
    tab, lo, hi = C.lee_cube(ruta)
    return lambda x: np.clip(C.aplica_cube(tab, lo, hi, entrada(x)), 0, 1)


def cubo_texto(f, n=33) -> str:
    g = np.linspace(0, 1, n)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")                      # R varía más rápido (formato Adobe)
    v = f(np.stack([r, gg, b], -1).reshape(-1, 3))
    return f"LUT_3D_SIZE {n}\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n" + "\n".join("%.6f %.6f %.6f" % tuple(p) for p in v) + "\n"


def q_de_cubo(texto: str) -> np.ndarray:
    return O.tabla_de_blob(U.referencia(texto))


def cubo_para_tabla(delta: np.ndarray, modelo: str, iteraciones: int = 3):
    """`.cube` 33³ tal que `lutsd` (referencia) devuelva ≈ `delta` [405,3] (unidades s7): se corrige por punto fijo la corrección de 2.ª diferencia de G90."""
    d = delta.astype(float)
    for _ in range(iteraciones + 1):
        f = lambda x, d=d.copy(): np.clip(C.ycc2rgb(C.rgb2ycc(x) + _interp(d, x, modelo)), 0, 1)
        texto = cubo_texto(f)
        q = q_de_cubo(texto)
        d = d + (delta - q)
    return texto, q


def _interp(d, x, modelo):
    u = C.rgb2ycc(x)
    idx, wt = O._estructura(x, modelo)
    return np.einsum("mk,mkc->mc", wt, (d * O.U)[idx])


def empaqueta(q: np.ndarray) -> bytes:
    """1064 B (405 nodos × 21 bits s7: Y<<14 | Cb<<7 | Cr) = el formato del blob de lutsd."""
    bits = 0
    for i, (a, b, c) in enumerate(q.astype(int).tolist()):
        bits |= (((a & 127) << 14) | ((b & 127) << 7) | (c & 127)) << (21 * i)
    return bits.to_bytes(U.TAM_TABLA, "little")


def ruido(f, sig=2 / 255, m=3000, seed=3):
    rng = np.random.default_rng(seed)
    p = np.array([[y, y, y] for y in (0.1, 0.2, 0.3, 0.5, 0.7, 0.85)] + [[.7, .3, .25], [.3, .6, .3], [.25, .35, .7], [.8, .65, .25], [.55, .35, .6], [.3, .6, .6]])
    x0 = np.repeat(p, m, 0)
    xn = np.clip(x0 + rng.normal(0, sig, x0.shape), 0, 1)
    return float((f(xn) - f(x0)).std(0).mean() / sig)


def main(carpeta: Path, salida: Path, nombres: list[str]) -> dict:
    salida.mkdir(parents=True, exist_ok=True)
    x, w = O.muestras()
    informe = {}
    de = lambda a, b: float(np.sum(w * C.de2000(a, b)))   # de2000 ya convierte RGB→Lab
    for n in nombres:
        f = objetivo(carpeta / f"Applelog_{n}.cube")
        y = f(x)
        q = O.ajusta_de(x, y, w, modelo=O.MODELO_DEFECTO)
        (salida / f"{n}.TAB").write_bytes(empaqueta(q))
        texto = cubo_texto(f)                                            # .cube = la película con la entrada horneada (muestreo directo en la cámara)
        (salida / f"{n}.cube").write_text(texto)
        q2 = q_de_cubo(texto)
        assert O.tabla_de_blob(empaqueta(q)).tolist() == q.tolist()
        fh = lambda z, q2=q2: np.clip(O.aplica(q2, z, O.MODELO_DEFECTO), 0, 1)
        fq = lambda z, q=q: np.clip(O.aplica(q, z, O.MODELO_DEFECTO), 0, 1)
        informe[n] = {"dE_TAB_vs_pelicula": de(fq(x), y), "dE_cube_directo_vs_pelicula": de(fh(x), y), "dE_pelicula_vs_entrada": de(y, x),
                      "ruido_pelicula": ruido(f), "ruido_TAB": ruido(fq), "nodos_recortados_%": float(np.mean(np.abs(q) >= 63) * 100)}
        print(n, {k: round(v, 2) for k, v in informe[n].items()}, flush=True)
    (salida / "informe.json").write_text(json.dumps(informe, indent=1))
    return informe


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:] or NOMBRES)
