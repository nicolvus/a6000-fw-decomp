#!/usr/bin/env python3
"""T9 — calibración del modelo de ISP con fotos de la cámara real: ΔE (CIE76) y diferencias por canal entre el modelo y la salida de la BIONZ X.

Dos entradas:
  * ARW de la A6000 (`compara_real.py DSC03773.ARW …`): el ARW lleva la vista previa JPEG que generó la propia BIONZ X a partir de ese RAW → par
    (RAW del sensor, salida real). El modelo recibe el RAW con negro restado, balance de blancos as-shot y matriz cámara→sRGB lineal (dcraw), SIN ISP de Sony.
    Lee del MakerNote el Creative Style, el DRO y la temperatura de color con que se hizo el disparo (la vista previa los incluye; el modelo no modela DRO).
  * Par JPEG: `--entrada original.jpg --foto camara.jpg` (misma escena; la entrada se trata como sRGB, APROX).
Además mide la curva tonal real (mediana de la vista previa por bandas de señal lineal) y busca la exposición de entrada `k` y la curva (`--barrido`) que mejor explican la salida.
Requiere .venv con numpy, Pillow y (solo ARW) rawpy. Uso: `.venv/bin/python scripts/gui/isp/compara_real.py DSC03773.ARW --barrido [--salida out.json]`.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import modelo as M

TAM = (1616, 1080)   # tamaño de la vista previa de la A6000
SRGB2XYZ = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
MAKER = {0xB020: "creative_style", 0xB021: "color_temp_K", 0xB025: "dro", 0xB026: "estabilizador", 0xB029: "color_mode", 0xB023: "scene_mode", 0xB024: "zone_matching"}


def lab(rgb: np.ndarray) -> np.ndarray:
    """sRGB [0,1] → CIELAB D65."""
    xyz = M.srgb_a_lineal(rgb) @ SRGB2XYZ.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def delta_e(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.linalg.norm(lab(a) - lab(b), axis=-1).ravel()
    c = ((a - b) * 255).reshape(-1, 3)
    return {"dE76_media": float(d.mean()), "dE76_mediana": float(np.median(d)), "dE76_p95": float(np.percentile(d, 95)),
            "dif_canal_RGB_8bit_media": [round(float(v), 2) for v in c.mean(0)], "dif_canal_RGB_8bit_abs": [round(float(v), 2) for v in np.abs(c).mean(0)]}


def maker_sony(b: bytes) -> dict:
    """Campos del MakerNote Sony (IFD sin cabecera; offsets desde el inicio del fichero TIFF) y del EXIF necesarios para saber con qué estilo se hizo el disparo."""
    def ifd(o: int) -> dict:
        n = struct.unpack_from("<H", b, o)[0]
        return {t: (ty, c, v, o + 10 + 12 * i) for i in range(n) for t, ty, c, v in [struct.unpack_from("<HHII", b, o + 2 + 12 * i)]}
    i0 = ifd(struct.unpack_from("<I", b, 4)[0])
    ex = ifd(i0[0x8769][2])
    out = {"iso": ex[0x8827][2]}
    for tag, nombre in ((0x829A, "exposicion_s"), (0x829D, "f")):
        n, d = struct.unpack_from("<II", b, ex[tag][2])
        out[nombre] = n / d
    ty, c, off, _ = ex[0x927C]
    for tag, (ty, c, v, pos) in ifd(off).items():
        if tag in MAKER:
            out[MAKER[tag]] = b[v:v + c].split(b"\0")[0].decode("latin1") if ty == 2 else v
    return out


def lee_arw(ruta: Path) -> tuple[np.ndarray, np.ndarray, dict]:
    import rawpy
    with rawpy.imread(str(ruta)) as r:
        s = r.sizes
        raw = r.raw_image[s.top_margin:s.top_margin + s.height, s.left_margin:s.left_margin + s.width].astype(np.float32)
        bl = np.array(r.black_level_per_channel, np.float32)
        wb = np.array(r.camera_whitebalance[:3], np.float32)
        wb /= wb[1]
        xyz2cam = np.array(r.rgb_xyz_matrix[:3], float)
        blanco = float(r.white_level)
        patron = r.raw_pattern.tolist()
        prev = np.asarray(Image.open(io.BytesIO(r.extract_thumb().data)).convert("RGB"), np.float32) / 255
    assert patron == [[0, 1], [3, 2]], patron   # RGGB; otro patrón: ampliar aquí
    R, G1, G2, B = raw[0::2, 0::2] - bl[0], raw[0::2, 1::2] - bl[1], raw[1::2, 0::2] - bl[3], raw[1::2, 1::2] - bl[2]
    cam = np.stack([R, (G1 + G2) / 2, B], -1) / (blanco - bl.max()) * wb       # media 2x2 (media resolución): sin demosaico
    rgb2cam = xyz2cam @ SRGB2XYZ
    rgb2cam /= rgb2cam.sum(1, keepdims=True)
    lin = np.clip(cam @ np.linalg.inv(rgb2cam).T, 0, None)
    a = np.asarray(Image.fromarray(lin.astype(np.float32)[..., 0]).resize(TAM, Image.BOX))
    lin_r = np.stack([a] + [np.asarray(Image.fromarray(lin[..., c].astype(np.float32)).resize(TAM, Image.BOX)) for c in (1, 2)], -1)
    prev = np.asarray(Image.fromarray((prev * 255).astype(np.uint8)).resize(TAM, Image.BOX), np.float32) / 255 if prev.shape[1::-1] != TAM else prev
    return lin_r, prev, maker_sony(ruta.read_bytes())


def curva_tonal(lin: np.ndarray, prev: np.ndarray, n: int = 24) -> list[list[float]]:
    """Mediana de la salida real (verde de la vista previa) por bandas logarítmicas de señal lineal (verde): [(lineal, salida 0-1, píxeles)]."""
    g, j = lin[..., 1].ravel(), prev[..., 1].ravel()
    e = np.geomspace(0.002, 1.0, n + 1)
    idx = np.digitize(g, e)
    out = []
    for b in range(1, n + 1):
        m = idx == b
        if m.sum() > 300:
            out.append([round(float(np.median(g[m])), 5), round(float(np.median(j[m])), 4), int(m.sum())])
    return out


def mejor_k(t: M.Tablas, lin: np.ndarray, prev: np.ndarray, p: dict, foto: bool) -> tuple[float, dict]:
    sub = (slice(None, None, 6), slice(None, None, 6))
    mejor = (1e9, 0.0)
    for k in np.geomspace(0.5, 24, 60):
        e = delta_e(M.aplica(lin[sub], p, t, foto, float(k), True), prev[sub])["dE76_media"]
        mejor = min(mejor, (e, float(k)))
    return mejor[1], delta_e(M.aplica(lin, p, t, foto, mejor[1], True), prev)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("fotos", nargs="*", type=Path, help="ARW de la A6000")
    ap.add_argument("--entrada", type=Path), ap.add_argument("--foto", type=Path)
    ap.add_argument("--gamma", type=int, default=5, help="valor app de Gamma (5 = Still: foto con Creative Style Standard); 2–11")
    ap.add_argument("--ajustes", type=json.loads, default={}, help='JSON de ajustes PP, p. ej. \'{"saturation":1}\'')
    ap.add_argument("--exposicion", type=float, help="k fijo (por omisión se busca el mejor)")
    ap.add_argument("--barrido", action="store_true", help="prueba todas las curvas y lista su ΔE")
    ap.add_argument("--salida", type=Path)
    a = ap.parse_args()
    t = M.Tablas()
    casos = []
    for f in a.fotos:
        lin, prev, meta = lee_arw(f)
        casos.append((f.name, lin, prev, meta, True))
    if a.entrada and a.foto:
        fo = Image.open(a.foto).convert("RGB")
        ent = np.asarray(Image.open(a.entrada).convert("RGB").resize(fo.size, Image.BOX), np.float32) / 255
        casos.append((a.foto.name, ent, np.asarray(fo, np.float32) / 255, {"entrada": a.entrada.name}, False))
    if not casos:
        ap.error("indica ARW o --entrada/--foto")
    res = {}
    for nombre, lin, prev, meta, es_lineal in casos:
        r = {"meta": meta, "curva_tonal_real": curva_tonal(lin if es_lineal else M.srgb_a_lineal(lin), prev)}
        gammas = [a.gamma] if not a.barrido else sorted(M.CURVA_VIDEO)
        r["modelo"] = {}
        for g in gammas:
            p = {**a.ajustes, "gamma": g}
            if a.exposicion:
                k, e = a.exposicion, delta_e(M.aplica(lin, p, t, True, a.exposicion, es_lineal), prev)
            elif es_lineal:
                k, e = mejor_k(t, lin, prev, p, True)
            else:
                k, e = 1.0, delta_e(M.aplica(lin, p, t, True, 1.0, False), prev)
            r["modelo"][f"{g}:{M.GAMMA_NOMBRES[g]}:{M.CURVA_VIDEO[g] if g != 5 else 'a6000_f00'}"] = {"k": round(k, 3), **e}
        res[nombre] = r
        print(f"{nombre} {meta}")
        for k_, v in r["modelo"].items():
            print(f"  gamma {k_:32s} k={v['k']:<6} ΔE76 media {v['dE76_media']:5.1f} mediana {v['dE76_mediana']:5.1f} p95 {v['dE76_p95']:5.1f} dif RGB {v['dif_canal_RGB_8bit_media']}")
    if a.salida:
        a.salida.write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
