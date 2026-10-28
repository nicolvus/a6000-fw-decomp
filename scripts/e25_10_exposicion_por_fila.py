#!/usr/bin/env python3
"""E25-10: tiempo efectivo de exposición por fila a partir de los ARW de camera_raw_exposure.py.

Modelo por banda de filas b: lineal_b(T) = s_b · (T + τ_b), con T = velocidad fijada (s), s_b = brillo de escena en esa banda
(incógnita) y τ_b = tiempo adicional que no controla la velocidad. Ajuste lineal lineal = a + c·T → τ = a/c.
Uso: e25_10_exposicion_por_fila.py DIR_T044 [BANDAS]"""
import glob
import json
import sys

import numpy as np
import rawpy

d = sys.argv[1]
nb = int(sys.argv[2]) if len(sys.argv) > 2 else 32
rows: dict[float, list[np.ndarray]] = {}
for f in sorted(glob.glob(f"{d}/*.ARW")):
    n, den = f.split("/")[-1].split("_r")[0].split("_")
    r = rawpy.imread(f)
    x = r.raw_image_visible.astype(np.float32) - np.mean(r.black_level_per_channel)
    k = x.shape[0] // nb
    rows.setdefault(int(n) / int(den), []).append(np.array([x[i * k:(i + 1) * k].mean() for i in range(nb)]))
T = np.array(sorted(rows))
L = np.array([np.mean(rows[t], axis=0) for t in T])  # [velocidades, bandas]
out = []
for b in range(nb):
    c, a = np.polyfit(T, L[:, b], 1)
    pred = a + c * T
    out.append({"banda": b, "tau_ms": round(1000 * a / c, 2), "escena": round(float(c), 1),
                "r2": round(float(1 - ((L[:, b] - pred) ** 2).sum() / ((L[:, b] - L[:, b].mean()) ** 2).sum()), 4),
                "err_max_pct": round(float(np.abs((L[:, b] - pred) / L[:, b]).max() * 100), 1)})
tau = np.array([o["tau_ms"] for o in out])
slope, icpt = np.polyfit(np.arange(nb), tau, 1)
print(f"{nb} bandas; τ arriba {tau[0]:.1f} ms, abajo {tau[-1]:.1f} ms; ajuste lineal τ = {icpt:.1f} + {slope:.2f}·banda ms "
      f"(rampa total {slope * (nb - 1):.1f} ms)")
print("R² mín", min(o["r2"] for o in out), " error máx %", max(o["err_max_pct"] for o in out))
for o in out[:: max(nb // 8, 1)]:
    print(o)
# Modelo alternativo: tiempo efectivo = max(T, floor_b)
alt = []
for b in range(nb):
    best = min((np.sum((L[:, b] - c * np.maximum(T, fl)) ** 2), fl) for fl in np.linspace(0.001, 0.12, 120)
                for c in [np.sum(L[:, b] * np.maximum(T, fl)) / np.sum(np.maximum(T, fl) ** 2)])
    alt.append(best[0])
print("residuo medio modelo aditivo", float(np.mean([np.sum((L[:, b] - np.polyval(np.polyfit(T, L[:, b], 1), T)) ** 2) for b in range(nb)])),
      "vs modelo max()", float(np.mean(alt)))
json.dump({"velocidades_s": T.tolist(), "bandas": out, "tau_lineal": {"ms_banda0": icpt, "ms_por_banda": slope}},
          open(f"{d}/e25_10_tau_por_fila.json", "w"), indent=1)
