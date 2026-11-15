"""G38-A — Silent por debajo del «piso» de 0,58 ms: extiende el tope de `r5` de `patch_silent_r5` (sin CFW; solo copias en memoria).

El piso de 0,58 ms NO sale de SetExposure (`0x436d6f6c`: `shd` es un campo de 14 bit sin clamp) ni del productor nativo (`0x4383fa40`:
`shd = max(suelo+L, VTS) − L`, sin mínimo de L): lo fija la cueva de R87 con `min(r5, 4218)` (`R5_FULL − 1`). Con la ley medida en R87,
E = 17,135 µs·(4252 − r5), el tope 4218 da E = 17,135·34 = 583 µs. Aquí el tope pasa a 4251 (E → 1 línea = 17 µs) y la base queda en 4252.
Hipótesis NO medida: que el sensor acepte `r5` > 4219 (T046 solo barrió ≤ 4200 y 4300 = sin efecto). Solo se valida en cámara (G38-C).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "g22"), str(Path(__file__).resolve().parents[1])]
import patch_silent_r5 as R

R5_BASE, R5_TOPE = 4252, 4251            # R87: E = 0 en r5 = 4252; tope = 1 línea de exposición


def _con_constantes(fn, *a, **k):
    old = (R.R5_FULL, R.R5_LAG)
    R.R5_FULL, R.R5_LAG = R5_TOPE + 1, R5_BASE - (R5_TOPE + 1)   # clamp = R5_FULL − 1 = 4251; base = FULL + LAG = 4252
    try:
        return fn(*a, **k)
    finally:
        R.R5_FULL, R.R5_LAG = old


def apply_bytes(data: bytes) -> bytes:
    return _con_constantes(R.apply_bytes, data)


def emular(img: bytes, tv: int, silent: int = 1):
    return R.emular(img, tv, silent)


def exposicion_us(r5: int, ley: str = "r87") -> float:
    """Exposición predicha para un r5: R87 (Silent medido) o T046 (barrido directo en RAM, ShutMode 0)."""
    return max(0.0, 17.135 * (4252 - r5)) if ley == "r87" else max(0.0, 15.2 * (4219 - r5))
