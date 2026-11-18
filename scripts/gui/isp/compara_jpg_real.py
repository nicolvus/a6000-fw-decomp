#!/usr/bin/env python3
"""E2E-8 — par RAW+JPG real de la MISMA escena (cámara, 17-11-2026) → revelado emulado (modelo.py) vs JPG de la BIONZ X a escala 1500×1000.
Métricas: ΔE76 (media/mediana/p95, por zonas), error medio por canal, histogramas (L*, canales), balance de blancos (relación R/G, B/G en neutros), curva tonal por bandas y nitidez/ruido en planos.
`--curva arw` usa la curva SR2 0x7802 del propio ARW (por omisión), `--curva std` la `sr2_standard` genérica. Uso: `.venv/bin/python scripts/gui/isp/compara_jpg_real.py DSC03986.ARW DSC03986.JPG [--salida out.json]`.
Requiere .venv (numpy, rawpy, Pillow, opencv, scipy)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import rawpy
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import compara_real as C
import modelo as M
import raw_entrada as R

UMBRAL_SENAL = 0.003   # lineal (verde) a partir del cual la señal domina al ruido a ISO 1000 (MEDIDO: p90 de la escena ≈ 0,005)
W, H = 1500, 1000   # JPG 6000×4000 reducido 4× con caja


def carga_par(arw: Path, jpg: Path) -> dict:
    """ARW+JPG → {lin: RGB lineal (negro, WB as-shot) alineado al JPG, jpg: 0-1, sr2, meta}. Alineación: ajuste radial por foto (el JPG lleva la corrección de lente de la BIONZ X)."""
    b = arw.read_bytes()
    s = R.sr2(b)
    with rawpy.imread(str(arw)) as r:
        raw = r.raw_image.copy()
    rgb = R.demosaico(raw, s[0x7310].astype(np.float32), s[0x7313].astype(np.float32) / 1024)
    grande = cv2.resize(rgb, (2 * W, 2 * H), interpolation=cv2.INTER_AREA)
    j = np.asarray(Image.open(jpg).convert("RGB").resize((W, H), Image.BOX), np.float32) / 255
    p, cc = R.ajusta_geometria(grande, j, 404, 270)
    return {"lin": R.alinea(grande, p, W, H), "jpg": j, "sr2": s, "geo": p.tolist(), "cc": cc, "meta": C.maker_sony(b)}


def tablas(s: dict, curva: str) -> M.Tablas:
    t = M.Tablas()
    return t.con_sr2(s[0x7802]) if curva == "arw" else t


def mide(par: dict, curva: str = "arw", k: float | None = None) -> dict:
    lin, j = par["lin"], par["jpg"]
    t = tablas(par["sr2"], curva)
    if k is None:
        k = 1.0
    out = M.aplica(lin, {"gamma": 5}, t, True, k, True)
    de = C.delta_e(out, j)
    la, lb = C.lab(out), C.lab(j)
    g = cv2.cvtColor(j, cv2.COLOR_RGB2GRAY)
    plano = cv2.dilate(np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1)), np.ones((9, 9))) < 0.03
    plano[:30] = plano[-30:] = False; plano[:, :30] = plano[:, -30:] = False
    neutro = plano & (np.hypot(lb[..., 1], lb[..., 2]) < 8) & (lb[..., 0] > 20) & (lb[..., 0] < 85)
    def wb(a): return [round(float(np.median(a[neutro][:, c] / np.maximum(a[neutro][:, 1], 1e-3))), 4) for c in (0, 2)] if neutro.sum() > 200 else None
    nitidez = lambda a: float(np.var(cv2.Laplacian(cv2.cvtColor(a.astype(np.float32), cv2.COLOR_RGB2GRAY), cv2.CV_32F)))
    ruido = lambda a: float(np.std(cv2.cvtColor(a.astype(np.float32), cv2.COLOR_RGB2GRAY)[plano] - cv2.GaussianBlur(cv2.cvtColor(a.astype(np.float32), cv2.COLOR_RGB2GRAY), (0, 0), 2)[plano])) if plano.sum() > 500 else None
    hist = lambda a, n=16: np.histogram(a, bins=n, range=(0, 1))[0] / a.size
    sen = cv2.GaussianBlur(lin[..., 1], (0, 0), 3) > UMBRAL_SENAL   # píxeles con señal (el resto es ruido de lectura, que la BIONZ X reduce y el modelo no)
    d = np.linalg.norm(la - lb, axis=-1)
    return {"k": k, **de, "senal": {"frac": round(float(sen.mean()), 3), "dE76_media": round(float(d[sen].mean()), 2), "dE76_mediana": round(float(np.median(d[sen])), 2),
                                    "dif_canal_RGB_8bit_media": [round(float(v), 2) for v in ((out - j) * 255)[sen].mean(0)]},
            "ruido_lectura": {"dE76_media": round(float(d[~sen].mean()), 2), "dL_media": round(float((la[..., 0] - lb[..., 0])[~sen].mean()), 2)}, "zonas": C.zonas(out, j), "dL_media": round(float((la[..., 0] - lb[..., 0]).mean()), 2),
            "dif_ab_media": [round(float((la[..., c] - lb[..., c]).mean()), 2) for c in (1, 2)],
            "wb_neutros_R/G_B/G": {"modelo": wb(out), "jpg": wb(j), "px": int(neutro.sum())},
            "hist_L_16_L1": round(float(np.abs(hist(la[..., 0] / 100) - hist(lb[..., 0] / 100)).sum()), 4),
            "hist_canal_L1": [round(float(np.abs(hist(out[..., c]) - hist(j[..., c])).sum()), 4) for c in range(3)],
            "curva_tonal": {"modelo": [[round(a, 4), round(b, 4)] for a, b, _ in C.curva_tonal(lin, out)], "jpg": [[round(a, 4), round(b, 4)] for a, b, _ in C.curva_tonal(lin, j)]},
            "nitidez_laplaciano": {"modelo": round(nitidez(out), 6), "jpg": round(nitidez(j), 6)},
            "ruido_plano_std": {"modelo": ruido(out), "jpg": ruido(j)}}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arw", type=Path), ap.add_argument("jpg", type=Path)
    ap.add_argument("--curva", choices=("arw", "std"), default="arw")
    ap.add_argument("--k", type=float), ap.add_argument("--salida", type=Path)
    a = ap.parse_args()
    par = carga_par(a.arw, a.jpg)
    r = {"meta": par["meta"], "geo": par["geo"], "cc": par["cc"], **mide(par, a.curva, a.k)}
    print(json.dumps({k: v for k, v in r.items() if k not in ("curva_tonal",)}, indent=1))
    if a.salida:
        a.salida.write_text(json.dumps(r, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
