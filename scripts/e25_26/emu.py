"""E25-26 — emulación end-to-end de C3-B sobre StartExposure real (offline).

Ejecuta el tramo real `0x438c828c-0x438c83e8` de la imagen combinada
(selector E25-24 + C3-B) y compara con el firmware original.  `SetExposure`,
`SetRead`, `SSB`, `Execute` y el imager son stubs que registran argumentos; no se
modela el IMX210.  El objetivo es demostrar qué valores llegan a `SetExposure` y
que EFCS no cambia.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/e25_18"))
sys.path.insert(0, str(ROOT / "scripts/e25_16"))

import secuencia as S
from emu_core import FW

VTS = 4219
CAP_FIELDS = {
    0x64C: (4, 0),
    0x650: (2, 0),
    0x655: (1, 0),
    0x504: (4, 0),
    0x740: (4, 1),
    0x4B9C: (4, 0),
    0x41C: (4, 0),
    0x5E0: (2, VTS),
}


def _cap(shd: int, svd: int, shutmode: int, flag: int, vts: int = VTS, cap504: int = 0) -> dict:
    cap = dict(CAP_FIELDS)
    cap[0x64C] = (4, shd)
    cap[0x650] = (2, svd)
    cap[0x655] = (1, shutmode)
    cap[0x41C] = (4, flag)
    cap[0x5E0] = (2, vts)
    cap[0x504] = (4, cap504)
    return cap


def run(data: bytes, *, flag: int, shd: int, svd: int, shutmode: int = 3, vts: int = VTS,
        cap504: int = 0, forzado: int = 0) -> dict:
    r = S.start_exposure(_cap(shd, svd, shutmode, flag, vts, cap504), forzado=forzado, data=data)
    mem = r.pop("mem")
    r["cap_64c_final"] = int.from_bytes(mem[0x64C:0x650], "little")
    r["cap_650_final"] = int.from_bytes(mem[0x650:0x652], "little")
    r["cap_655_final"] = mem[0x655]
    r["cap_41c"] = int.from_bytes(mem[0x41C:0x420], "little")
    return r


def baseline(**kw) -> dict:
    return run(FW.read_bytes(), **kw)


def equivalent(a: dict, b: dict) -> bool:
    keys = ("shd_a_SetExposure", "svd_a_SetExposure", "shutmode_a_SetExposure", "param_bytes",
            "cap650_final", "cap655_final", "cap73b")
    return all(a[k] == b[k] for k in keys)


def matrix(combined: bytes) -> dict[str, Any]:
    """Casos A/B/C/D de E25-26."""
    out: dict[str, Any] = {}
    # Caso A — EFCS: plan nativo con predicado 1 (1/4000)
    for cap504 in (0, 1):
        key = f"efcs_pred1_{'svd0' if cap504 else 'svd1'}"
        out[key] = {"original": baseline(flag=0, shd=8422, svd=1, shutmode=3, cap504=cap504),
                    "combined": run(combined, flag=0, shd=8422, svd=1, shutmode=3, cap504=cap504)}
    # Caso B — Electronic: mismo plan nativo
    out["electronic_pred1"] = {"original": baseline(flag=1, shd=8422, svd=1, shutmode=3),
                               "combined": run(combined, flag=1, shd=8422, svd=1, shutmode=3)}
    # Predicado 0 nativo (shd ya normalizado)
    out["electronic_pred0"] = {"original": baseline(flag=1, shd=4203, svd=0, shutmode=3),
                               "combined": run(combined, flag=1, shd=4203, svd=0, shutmode=3)}
    out["efcs_pred0"] = {"original": baseline(flag=0, shd=4203, svd=0, shutmode=3),
                         "combined": run(combined, flag=0, shd=4203, svd=0, shutmode=3)}
    # Ruta larga: no debe tocarse
    out["electronic_long"] = {"original": baseline(flag=1, shd=1, svd=2, shutmode=3),
                              "combined": run(combined, flag=1, shd=1, svd=2, shutmode=3)}
    # Bloque forzado (0x43a12c64 = 2): shd=2, svd=0, ShutMode=0
    out["forced_block"] = {"original": baseline(flag=1, shd=2, svd=0, shutmode=0, forzado=2),
                           "combined": run(combined, flag=1, shd=2, svd=0, shutmode=0, forzado=2)}
    # Errores: modalidad inválida, VTS cero, shd <= VTS
    out["invalid_flag"] = {"original": baseline(flag=2, shd=8422, svd=1, shutmode=3),
                           "combined": run(combined, flag=2, shd=8422, svd=1, shutmode=3)}
    out["zero_vts"] = {"original": baseline(flag=1, shd=8422, svd=1, shutmode=3, vts=0),
                       "combined": run(combined, flag=1, shd=8422, svd=1, shutmode=3, vts=0)}
    out["underflow"] = {"original": baseline(flag=1, shd=100, svd=1, shutmode=3, vts=4219),
                        "combined": run(combined, flag=1, shd=100, svd=1, shutmode=3, vts=4219)}
    # Alternancia EFCS -> Electronic -> EFCS -> Electronic
    seq = []
    for flag in (0, 1, 0, 1):
        d = run(combined, flag=flag, shd=8422, svd=1, shutmode=3)
        seq.append({"flag": flag, "shd": d["shd_a_SetExposure"], "svd": d["svd_a_SetExposure"],
                    "shutmode": d["shutmode_a_SetExposure"]})
    out["alternation"] = seq
    # Comparaciones
    out["efcs_identical"] = all(
        equivalent(v["original"], v["combined"]) for k, v in out.items()
        if isinstance(v, dict) and k.startswith("efcs"))
    out["errors_identical"] = all(
        equivalent(out[k]["original"], out[k]["combined"]) for k in ("invalid_flag", "zero_vts", "underflow", "forced_block"))
    out["electronic_normalized"] = (
        out["electronic_pred1"]["combined"]["shd_a_SetExposure"] == 4203
        and out["electronic_pred1"]["combined"]["svd_a_SetExposure"] == 0
        and out["electronic_pred1"]["combined"]["shutmode_a_SetExposure"] == 0)
    return out
