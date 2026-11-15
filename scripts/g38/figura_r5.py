"""G38: E frente a r5 con las dos calibraciones (T046 directa en RAM; R87 Silent) y el tope de la cueva. Salida: docs/gui/img/g38-r5-ley.png"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
t046 = [(1000, 49.1), (2000, 33.8), (3000, 18.5), (3500, 10.9), (4000, 3.3), (4100, 1.8), (4200, 0.3)]          # e25-10 §3 (ms)
r87 = [(4252 - round(t / 17.135), s * t / 1000) for t, s in [(775, 1.095), (1953, 1.003), (3906, 0.928), (9834, 1.091), (19668, 1.004)]]  # r87e
fig, ax = plt.subplots(figsize=(7, 4.2))
xs = range(3000, 4260)
ax.plot(xs, [max(0, 15.2 * (4219 - x)) / 1000 for x in xs], label="T046: 15,2 µs·(4219 − r5)")
ax.plot(xs, [max(0, 17.135 * (4252 - x)) / 1000 for x in xs], label="R87: 17,135 µs·(4252 − r5)")
ax.scatter(*zip(*[p for p in t046 if p[0] >= 3000]), c="C0", marker="o", label="T046 medido (RAW)")
ax.scatter(*zip(*r87), c="C1", marker="s", label="R87 medido (Silent/mecánico × T)")
ax.axvline(4218, c="k", ls="--", lw=1)
ax.text(4150, 6.5, "tope actual\nr5 ≤ 4218", ha="right", fontsize=8)
ax.axvspan(4219, 4251, color="C3", alpha=0.15)
ax.text(4235, 3.0, "sin medir", rotation=90, va="center", ha="center", fontsize=8)
ax.set_yscale("symlog", linthresh=0.1)
ax.set_xlim(3000, 4260); ax.set_ylim(0, 25)
ax.set_xlabel("r5"); ax.set_ylabel("exposición (ms)"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(ROOT / "docs/gui/img/g38-r5-ley.png", dpi=130)
