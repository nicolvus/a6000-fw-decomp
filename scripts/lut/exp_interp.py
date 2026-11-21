"""G90 §A — experimento mínimo de cámara que decide la interpolación de la LUT 3D del BIONZ X (trilineal / tetraédrica / otra).

Idea: una tabla con UN solo nodo alterado (N = Y 128, Cb 0, Cr 0; ΔCb = +40 uds) responde alrededor de N con una «pirámide» cuya forma depende del modelo:
  - 1 eje activo (rampa de gris en Y): idéntica en ambos modelos (1−|t|) → calibra la escala (anchura = 1 celda).
  - 2 ejes con el mismo signo (Cb y Cr a la vez): trilineal (1−t)², tetraédrica 1−t.
  - 3 ejes con el mismo signo: trilineal (1−t)³, tetraédrica 1−t.
  - 2 ejes con signo opuesto: trilineal (1−t)², tetraédrica (1−2t)₊ (se anula en t=0,5; depende de la diagonal 000→111 elegida por el hardware).
  - vecino más cercano: escalón (1 hasta t=1 y 0 después).
Se compara la respuesta MEDIDA (JPG con la tabla − JPG con tabla cero, misma escena/RAW) con las predicciones. `decide()` ajusta el exponente p de A·(1−|t|)^p
por rampa; trilineal ⇒ p ≈ nº de ejes, tetraédrica ⇒ p ≈ 1.
uso: exp_interp.py DIRECTORIO  → tabla.bin (0x654 B, nodo N), ramp_*.png (imágenes a fotografiar/revelar), predicciones.json.
shortcut: ramas con la diagonal 000→111 en el orden (Y, Cb, Cr); si el hardware usa otra, la rampa de signo opuesto lo revela (la respuesta no se anula donde se predice).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import cube_a6000 as C
import lut_opt as O

NODO = (2, 4, 4)            # Y 128, Cb 0, Cr 0
DELTA = (0, 40, 0)          # ΔCb = +40 uds (≈ 0,117 de rango: ΔE de decenas en el nodo)
RAMPAS = {                  # nombre: (dirección en (Y, Cb, Cr) en unidades de celda; ejes activos)
    "y": ((1, 0, 0), 1),
    "cbcr_igual": ((0, 1, 1), 2),
    "cbcr_opuesto": ((0, 1, -1), 2),
    "ycbcr_igual": ((1, 1, 1), 3),
}
H = np.array([0.25, 0.125, 0.125])     # paso de celda en (Y, Cb, Cr), unidades normalizadas


def tabla_un_nodo() -> np.ndarray:
    q = np.zeros((C.N, 3), np.int8)
    q[NODO[0] * 81 + NODO[1] * 9 + NODO[2]] = DELTA
    return q


def ycc_nodo() -> np.ndarray:
    return np.array([NODO[0] / 4, (NODO[1] - 4) / 8, (NODO[2] - 4) / 8])


def ramp_ycc(d, t: np.ndarray) -> np.ndarray:
    """Puntos YCC de la rampa t∈[−1,1] (t = fracción de celda desde N en la dirección d)."""
    return ycc_nodo() + t[:, None] * np.array(d) * H


def respuesta(d, t, modelo) -> np.ndarray:
    """ΔCb que añade la tabla (unidades normalizadas) a lo largo de la rampa, por modelo ('tri', 'tetra', 'cercano')."""
    q = tabla_un_nodo()
    u = ramp_ycc(d, t)
    if modelo == "cercano":
        g = np.column_stack([u[:, 0] * 4, (u[:, 1] + .5) * 8, (u[:, 2] + .5) * 8])
        k = np.round(g).astype(int)
        return (q[k @ np.array([81, 9, 1])] * O.U)[:, 1]
    idx, w = O.pesos_m(u, modelo)
    return np.einsum("mk,mk->m", w, (q.astype(float) * O.U)[idx][..., 1])


def predicciones(n=41) -> dict:
    t = np.linspace(-1, 1, n)
    return {nom: {m: respuesta(d, t, m).round(5).tolist() for m in ("tri", "tetra", "cercano")} for nom, (d, _) in RAMPAS.items()} | {"t": t.tolist()}


def decide(medidas: dict[str, tuple[np.ndarray, np.ndarray]]) -> dict:
    """medidas[rampa] = (t, respuesta ΔCb medida) con t en celdas desde N (si solo hay posición, ajustar antes s0 y w con la rampa «y»).
    Ajusta A·max(1−|t|,0)^p por rampa (cuadrados mínimos sobre una rejilla de p) y devuelve p y el veredicto por exponentes esperados."""
    out: dict[str, Any] = {}
    for nom, (t, r) in medidas.items():
        base = np.clip(1 - np.abs(t), 0, None)
        mejor: tuple[float, float, float] = (float("inf"), 0.0, 0.0)
        for p in np.linspace(0.3, 4.0, 75):
            f = base ** p
            a = (f @ r) / (f @ f)
            e = float(np.sqrt(np.mean((r - a * f) ** 2)))
            if e < mejor[0]:
                mejor = (e, float(p), float(a))
        out[nom] = {"p": mejor[1], "A": mejor[2], "rms": mejor[0], "n_ejes": RAMPAS[nom][1]}
    ej = {k: v for k, v in out.items() if k in ("cbcr_igual", "ycbcr_igual")}
    p_med = np.mean([v["p"] / v["n_ejes"] for v in ej.values()]) if ej else float("nan")
    out["veredicto"] = "trilineal" if p_med > 0.75 else "tetraedrica" if (ej and np.mean([v["p"] for v in ej.values()]) < 1.3) else "indeterminado"
    return out


def imagen_rampa(nom: str, ancho=1200, alto=200) -> np.ndarray:
    """Imagen sRGB 8 bit: la rampa de −1.5 a +1.5 celdas centrada en N, con YCC→RGB BT.601 (cadena neutra: la posición exacta la libera el ajuste de s0, w)."""
    d, _ = RAMPAS[nom]
    t = np.linspace(-1.5, 1.5, ancho)
    rgb = np.clip(C.ycc2rgb(ramp_ycc(d, t)), 0, 1)
    return (np.repeat(rgb[None], alto, 0) * 255 + .5).astype(np.uint8)


def main(destino: Path) -> None:
    from PIL import Image
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "tabla.bin").write_bytes(C.empaqueta_hw(tabla_un_nodo()))
    (destino / "tabla_cero.bin").write_bytes(C.empaqueta_hw(np.zeros((C.N, 3), np.int8)))
    for nom in RAMPAS:
        Image.fromarray(imagen_rampa(nom)).save(destino / f"ramp_{nom}.png")
    (destino / "predicciones.json").write_text(json.dumps(predicciones()))
    print(f"escrito en {destino}: tabla.bin (nodo {NODO}, Δ={DELTA}), tabla_cero.bin, ramp_*.png, predicciones.json")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
