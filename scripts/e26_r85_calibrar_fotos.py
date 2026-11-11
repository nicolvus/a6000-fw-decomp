#!/usr/bin/env python3
"""E26-R85 — Calibración del obturador desde tripletas de fotos ARW (Silent / EFCS activado / EFCS desactivado), misma escena.

Por tripleta: cociente lineal (sin negro) frente a EFCS desactivado = mediana de cocientes por bloque de 32×32 (bloques no saturados y
con señal), global y en 8 bandas horizontales. EFCS: con la tabla `c` que había en la NVRAM (`--c-previo`, por defecto la de prueba
de R84, 2000 µs), pérdida = T' − E_on con T' = T + c (T de Darwin, `0x19a12` emulado, medio paso EV); con esos puntos
(x = B − A, pérdida) y la cola de R62/R74 (pérdida 0 desde x = 4570 µs) construye la tabla v3 (`G+0x48`) para 1/4000…1/30.
Silent: exposición efectiva = T · cociente (ms).
Uso: e26_r85_calibrar_fotos.py DIR SILENT,ON,OFF [SILENT,ON,OFF ...] [--c-previo 2000] [--out TABLA.json]
     e26_r85_calibrar_fotos.py selftest
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "e26_r76"))
import e26_r76_parche_darwin_tabla as P

BLK, NB = 32, 8
COLA = [(4570, 0.0), (7670, 0.0)]          # R62 §2 / R74 §4: sin pérdida desde B − A ≈ 4,5 ms (modelo R82)


def t_darwin(seg: float) -> int:
    """T (µs) que usa Darwin para la velocidad nominal `seg` en el escalón de 1/2 o 1/3 EV más cercano."""
    img = P.DARWIN.read_bytes()
    ev = math.log2(1 / seg)
    k2, k3 = round(2 * ev), round(3 * ev)
    tv = 0x1000 + (128 * k2 if abs(k2 / 2 - ev) <= abs(k3 / 3 - ev) else round(256 * k3 / 3))
    return P.t_us(img, tv)


def bloques(path: Path):
    import numpy as np
    import rawpy
    with rawpy.imread(str(path)) as r:
        a = r.raw_image_visible.astype(np.float64)
        blk, wl = float(np.mean(r.black_level_per_channel)), float(r.white_level)
    h, w = (a.shape[0] // BLK) * BLK, (a.shape[1] // BLK) * BLK
    a = a[:h, :w].reshape(h // BLK, BLK, w // BLK, BLK)
    return (a.mean((1, 3)) - blk) / (wl - blk), a.max((1, 3)) >= wl * 0.97


def cociente(num, den, mask):
    import numpy as np
    h = num.shape[0]
    tot = float(np.median(num[mask] / den[mask])) if mask.sum() > 50 else float("nan")
    bandas = []
    for i in range(NB):
        s = slice(i * h // NB, (i + 1) * h // NB)
        m = mask[s]
        bandas.append(round(float(np.median(num[s][m] / den[s][m])), 3) if m.sum() > 5 else None)
    return tot, bandas


def exposicion(path: Path) -> float:
    import exifread
    with open(path, "rb") as f:
        v = exifread.process_file(f, details=False)["EXIF ExposureTime"].values[0]
    return v.num / v.den


def medir(d: Path, trip: list[str]) -> dict:
    s, on, off = (d / f"{n}.ARW" for n in trip)
    seg = exposicion(off)
    assert exposicion(s) == exposicion(on) == seg, f"velocidades distintas en {trip}"
    (ls, ss), (lo, so), (lf, sf) = bloques(s), bloques(on), bloques(off)
    ok = (lf > 0.003) & ~so & ~sf
    r_on, b_on = cociente(lo, lf, ok)
    r_s, b_s = cociente(ls, lf, ok & ~ss)
    t = t_darwin(seg)
    return {"fotos": trip, "velocidad": f"1/{round(1 / seg)}", "t_darwin_us": t, "on_off": round(r_on, 4), "on_off_bandas": b_on,
            "silent_off": round(r_s, 3), "silent_off_bandas": b_s, "silent_ms": round(t * r_s / 1000, 1),
            "silent_saturado": round(float(ss.mean()), 3)}


def puntos(medidas: list[dict], c_previo: int) -> list[tuple[float, float]]:
    pts: dict[float, list[float]] = {}
    for m in medidas:
        t = m["t_darwin_us"]
        x = P.separacion(t + c_previo)
        if x is not None and x < COLA[0][0]:   # R85b: desde 1/125 (x ≥ 6384) c no cambia nada (on/off = 1,00 con c = 2000): cola, no pérdida
            pts.setdefault(x, []).append(t + c_previo - m["on_off"] * t)     # pérdida = T' − E_on
    return sorted((x, statistics.mean(v)) for x, v in pts.items())


def curva(pts: list[tuple[float, float]]):
    xs, ds = zip(*(pts + COLA))
    return lambda x: P.perdida(x, list(xs), list(ds))     # plana por debajo del primer punto (hacia lo más rápido)


def velocidades() -> list[int]:
    img = P.DARWIN.read_bytes()
    ts = {P.t_us(img, 0x1000 + 128 * k) for k in range(10, 25)}                      # 1/2 EV: 1/30 … 1/4000
    ts |= {P.t_us(img, 0x1000 + round(256 * k / 3)) for k in range(15, 37)}         # 1/3 EV: 1/30 … 1/4000
    return sorted(ts)


def tabla(pts) -> tuple[list[tuple[int, int]], dict]:
    f = curva(pts)
    ts = velocidades()
    tab = P.construir_tabla(ts, perd=f)
    c_de = lambda t: next((c for tm, c in tab if t <= tm), 0)
    pred = {t: round(P.exposicion_real(t + c_de(t), f) / t, 3) for t in ts}
    return tab, pred


def selftest() -> None:
    pts = [(-1056.0, 1001.0), (1333.0, 1162.0)]
    tab, pred = tabla(pts)
    assert len(tab) <= P.TAB_MAX and all(0 <= c <= P.C_MAX for _, c in tab)
    malos = {t: e for t, e in pred.items() if abs(1 - e) > 0.06 and not P.WIN_LO - 300 <= t <= P.WIN_HI}
    assert not malos, malos
    assert abs(pred[345] - 1) < 0.03 and abs(pred[2761] - 1) < 0.03, pred
    print("selftest OK:", tab)


def main(argv: list[str]) -> None:
    if argv[:1] == ["selftest"]:
        return selftest()
    c_prev = int(argv[argv.index("--c-previo") + 1]) if "--c-previo" in argv else 2000
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--c-previo", "--out"))]
    d = Path(pos[0])
    medidas = [medir(d, [f"DSC0{n}" if n.isdigit() else n for n in t.split(",")]) for t in pos[1:]]
    pts = puntos(medidas, c_prev)
    tab, pred = tabla(pts)
    res = {"c_previo": c_prev, "medidas": medidas, "puntos": pts, "tabla": tab,
           "exposicion_predicha_E_sobre_T": {str(t): e for t, e in pred.items()}}
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if out:
        out.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
