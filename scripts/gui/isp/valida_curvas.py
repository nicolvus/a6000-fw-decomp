#!/usr/bin/env python3
"""T9 — valida las curvas extraídas: forma/rango y ajuste contra curvas públicas (BT.709 OETF y S-Log2) con la escala de entrada `k` libre.

La entrada de cada LUT (2048 pt) no está normalizada a reflectancia conocida (NO_VERIFICADO), por eso `k` se ajusta: un RMSE bajo con un `k` plausible es indicio de
identidad, no prueba. Las fórmulas públicas están escritas de memoria de las notas técnicas de Sony/ITU y NO constan en el repo (fuente a confirmar):
  BT.709: V = 4.5 L (L < 0.018), 1.099 L^0.45 − 0.099.
  S-Log3 (Sony): y = (420 + 261.5·log10((x+0.01)/0.19))/1023 (x ≥ 0.01125), lineal por debajo (95 en x = 0).
  S-Log2 (Sony): y = 0.432699·log10(155·x/219 + 0.037584) + 0.616596 + 0.03, x = reflectancia relativa (18 % gris → ≈ 0.32–0.34 de escala completa).
Salida: analysis/gui/isp/validacion_curvas.json y tabla por pantalla. Uso: valida_curvas.py"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo as M

X = np.arange(M.N_LUT) / (M.N_LUT - 1)
r709 = lambda l: np.where(l < 0.018, 4.5 * l, 1.099 * np.power(np.maximum(l, 1e-9), 0.45) - 0.099)
slog2 = lambda x: 0.432699 * np.log10(155 * x / 219 + 0.037584) + 0.616596 + 0.03


def slog3(x):
    return np.where(x >= 0.01125, (420 + 261.5 * np.log10(np.maximum(x + 0.01, 1e-9) / 0.19)) / 1023, (x * (171.2102946929 - 95) / 0.01125 + 95) / 1023)


def ajusta(c: np.ndarray, f) -> tuple[float, float]:
    mejor = (9.0, 0.0)
    for k in np.geomspace(0.02, 64, 500):
        e = float(np.sqrt(np.mean((np.clip(f(X * k), 0, 1)[8:] - c[8:]) ** 2)))
        mejor = min(mejor, (e, float(k)))
    return mejor


def valida(t: M.Tablas) -> dict:
    out = {}
    for k, c in sorted(t.curvas.items()):
        c = c.astype(float) / 1023
        e7, k7 = ajusta(c, r709)
        es, ks = ajusta(c, slog2)
        e3, k3 = ajusta(c, slog3)
        out[k] = {"min": round(float(c.min()), 4), "max": round(float(c.max()), 4), "monotona": bool((np.diff(c) >= 0).all()), "negro_cod10": round(c[0] * 1023),
                  "rmse_bt709": round(e7, 4), "k_bt709": round(k7, 3), "rmse_slog2": round(es, 4), "k_slog2": round(ks, 3), "rmse_slog3": round(e3, 4), "k_slog3": round(k3, 3)}
    return out


if __name__ == "__main__":
    r = valida(M.Tablas())
    (M.DIR / "validacion_curvas.json").write_text(json.dumps(r, indent=1))
    for k in ("a6000_v0a", "a6000_f00", "a7s_v16", "a7s_v18", "a7s_v19", "a7s_v1a", "a7s_v1b", "a7s_v1c", "a7s_v1d", "a6300_v1f"):
        v = r[k]
        print(f"{k:10s} máx {v['max']:.3f} negro {v['negro_cod10']:3d}  BT709 rmse {v['rmse_bt709']:.3f} (k {v['k_bt709']:.2f})  S-Log2 rmse {v['rmse_slog2']:.3f} (k {v['k_slog2']:.2f})  S-Log3 rmse {v['rmse_slog3']:.3f} (k {v['k_slog3']:.2f})")
