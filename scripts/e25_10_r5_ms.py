#!/usr/bin/env python3
"""E25-10: convierte bandas.json de camera_r5_raw.py en milisegundos de exposición efectiva por banda.

Las referencias sin parche (modo normal) ajustan por banda lineal = s·(T + τ); con s (escena) se divide el RAW parcheado:
exposición_ms = 1000·lineal/s. Uso: e25_10_r5_ms.py DIR_T046"""
import json
import sys

import numpy as np

d = sys.argv[1]
j = json.load(open(f"{d}/bandas.json"))  # noqa: SIM115
nb, res = j["nb"], j["resultados"]
ref = [r for r in res if r["modo"] == "normal"]
T, L = np.array([r["T"] for r in ref]), np.array([r["bandas"] for r in ref])
fit = [np.polyfit(T, L[:, b], 1) for b in range(nb)]
s = np.array([f[0] for f in fit])
tau = 1000 * np.array([f[1] for f in fit]) / s
print(f"referencia: τ arriba {tau[0]:.1f} ms, abajo {tau[-1]:.1f} ms")
rows = []
for r in (x for x in res if x["modo"] == "sm0"):
    e = 1000 * np.array(r["bandas"]) / s
    octs = [round(float(e[i * nb // 8:(i + 1) * nb // 8].mean()), 1) for i in range(8)]
    rows.append({"T": r["T"], "r5": r["r5"], "media_ms": float(e.mean()), "octavos_ms": octs})
    print(f"T=1/{round(1 / r['T']):<4} r5={r['r5']!s:>5} media={e.mean():6.1f} ms octavos={octs}")
pts = [(x["r5"], x["media_ms"]) for x in rows if abs(x["T"] - 1 / 250) < 1e-6 and x["r5"] and 2000 <= x["r5"] <= 4200]
c = np.polyfit(*zip(*pts), 1)
print(f"1/250: dE/dr5 = {c[0] * 1000:.1f} µs/unidad; exposición nula en r5 = {-c[1] / c[0]:.0f}")
with open(f"{d}/e25_10_r5_ms.json", "w") as fh:
    json.dump({"tau_ref_ms": tau.tolist(), "filas": rows, "us_por_unidad_r5": c[0] * 1000, "r5_cero": -c[1] / c[0]}, fh, indent=1)
