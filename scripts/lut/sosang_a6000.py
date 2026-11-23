#!/usr/bin/env python3
"""G97 — los 38 looks de «sosang LUT Studio» (spektrafilm: 29 películas con su copia recomendada + 9 simulaciones Fujifilm) llevados a la A6000.

Los `.cube` del sitio esperan una LUMIX (V-Log/V-Gamut o el estilo STD de la S1II); sobre la señal de la A6000 no valen tal cual. Cadena:
1. **Adaptador A6000 → escena** (`ajusta_adaptador`): con pares (JPEG embebido = render Estándar de la cámara, RAW = escena lineal XYZ D65) de las ARW
   se ajusta escena = s · M · g(x) (g = curva 1D monótona compartida, M 3×3). Ancla ISO 12232 (SOS): 18 % gris → 118/255.
2. **Objetivo** (`objetivo`): escena → V-Gamut → V-Log → `.cube` VLOG de la película (spektrafilm + papel recomendado). Las simulaciones Fujifilm solo
   existen para STD: escena → V-Log → inversa del adaptador del sitio `S1IIS2V` (STD → V-Log) → `.cube` STD.
3. **Hardware** (`ajusta_look`): T 1D tras la gamma (1024 u16, LUT-T-1) + LUT 5×9×9 ajustadas en ΔE2000 (`cube_a6000.descompone`); se elige con o sin T.
4. **Prueba** (`prueba`): sobre una ARW, la cámara simulada (JPEG embebido → T → LUT) frente a la película aplicada a la escena del RAW.
shortcut: la entrada de la LUT en cámara se toma como el JPEG Estándar (la LUT de fábrica del estilo Estándar se supone ≈ identidad; LUT-T-2 lo mide).
uso: sosang_a6000.py SALIDA [--arw FOTO.ARW] [--fotos CARPETA_ARW] [--solo id,id]
"""
from __future__ import annotations

import io
import json
import struct
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
import cube_a6000 as C
import tono_post

DATOS = ROOT / "luts/sosang"
GRIS_DISPLAY = 118 / 255                      # ISO 12232 SOS: 18 % → 118 en sRGB
VGAMUT_XYZ = np.array([[0.679644, 0.152211, 0.118600], [0.260686, 0.774894, -0.035580], [-0.009310, -0.004612, 1.102980]])
XYZ_VGAMUT = np.linalg.inv(VGAMUT_XYZ)
NODOS_G = np.linspace(0, 1, 25)


def vlog(lin: np.ndarray) -> np.ndarray:
    lin = np.maximum(lin, -0.02)
    return np.where(lin < 0.01, 5.6 * lin + 0.125, 0.241514 * np.log10(np.maximum(lin, 0.01) + 0.00873) + 0.598206)


def catalogo() -> list[dict]:
    """[{id, nombre, papel, vlog|None, std}] en el orden del sitio (películas y después simulaciones Fujifilm)."""
    out = []
    for l in (DATOS / "lista.tsv").read_text().splitlines():
        i, n, _, _, _, papel = l.split("\t")
        v = DATOS / "vlog" / f"{i}.cube"
        out.append({"id": i, "nombre": n, "papel": None if papel in ("-", "None") else papel, "vlog": v if v.exists() else None, "std": DATOS / "std" / f"{i}.cube"})
    return out


# ---------- pares de la cámara ----------
def par(arw: Path, paso: int = 8) -> tuple[np.ndarray, np.ndarray]:
    """(x [H,W,3] JPEG embebido en 0…1, XYZ [H,W,3] lineal del RAW registrado sobre el JPEG) a la resolución del JPEG / `paso` (media por bloques)."""
    import rawpy
    from PIL import Image
    with rawpy.imread(str(arw)) as r:
        jpg = Image.open(io.BytesIO(r.extract_thumb().data)).convert("RGB")
        xyz = r.postprocess(output_color=rawpy.ColorSpace.XYZ, gamma=(1, 1), no_auto_bright=True, use_camera_wb=True, output_bps=16, half_size=True, user_flip=0)
    x = np.asarray(jpg, float) / 255
    xyz = registra(xyz.astype(np.float32) / 65535, x)
    return _bloques(x, paso), _bloques(xyz, paso)


def registra(xyz: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Lleva el RAW a la geometría del JPEG: el JPEG trae corregida la distorsión del objetivo. Modelo radial (k1, k2) + escala + traslación
    ajustado a correspondencias SIFT (mínimos cuadrados robustos); `cv2.remap` del RAW."""
    import cv2
    from scipy.optimize import least_squares
    h, w = x.shape[:2]
    H, W = xyz.shape[:2]
    a = (np.clip(C.de_lineal(xyz[..., 1] / max(np.percentile(xyz[..., 1], 99), 1e-6)), 0, 1) * 255).astype(np.uint8)
    b = (x @ np.array([0.2126, 0.7152, 0.0722]) * 255).astype(np.uint8)
    sift = cv2.SIFT_create(4000)
    ka, da = sift.detectAndCompute(a, None)
    kb, db = sift.detectAndCompute(b, None)
    m = [p for p, q in cv2.BFMatcher().knnMatch(db, da, k=2) if p.distance < 0.75 * q.distance]
    pb = np.array([kb[p.queryIdx].pt for p in m])
    pa = np.array([ka[p.trainIdx].pt for p in m])
    c, nrm = np.array([w / 2, h / 2]), np.hypot(w / 2, h / 2)

    def mapa(p, u):
        d = (u - c) / nrm
        r2 = (d ** 2).sum(-1, keepdims=True)
        return (d * (1 + p[0] * r2 + p[1] * r2 ** 2) * p[2] * nrm) + np.array([W / 2, H / 2]) + p[3:5]
    p = least_squares(lambda p: (mapa(p, pb) - pa).ravel(), [0, 0, W / w, 0, 0], loss="soft_l1", f_scale=2).x
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    mp = mapa(p, np.stack([xx, yy], -1)).astype(np.float32)
    return np.stack([cv2.remap(np.ascontiguousarray(xyz[..., k]), mp[..., 0], mp[..., 1], cv2.INTER_AREA if False else cv2.INTER_LINEAR) for k in range(3)], -1).astype(float)


def _redim(a: np.ndarray, tam) -> np.ndarray:
    from PIL import Image
    return np.stack([np.asarray(Image.fromarray(a[..., c]).resize(tam, Image.BOX), float) for c in range(3)], -1)


def _bloques(a: np.ndarray, p: int) -> np.ndarray:
    h, w = a.shape[0] // p * p, a.shape[1] // p * p
    return a[:h, :w].reshape(h // p, p, w // p, p, 3).mean((1, 3))


def _g(theta: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Curva display → lineal monótona: incrementos exp(θ) sobre 25 nodos, interpolación lineal."""
    inc = np.exp(theta)
    nod = np.r_[0, np.cumsum(inc)]
    return np.interp(x, NODOS_G, nod)


def ajusta_adaptador(arws: list[Path]) -> dict:
    """Ajusta g (25 nodos), M (3×3) y una ganancia por foto; devuelve el adaptador normalizado al ancla SOS."""
    from scipy.optimize import least_squares
    xs, ys, ids = [], [], []
    for k, a in enumerate(arws):
        x, y = par(a)
        h, w = x.shape[:2]
        sl = (slice(h // 6, h - h // 6), slice(w // 6, w - w // 6))             # sin esquinas: la cámara corrige viñeteo y distorsión en el JPEG
        x, y = x[sl].reshape(-1, 3), y[sl].reshape(-1, 3)
        ok = np.all((x > 0.02) & (x < 0.96), 1) & np.all(y > 1e-5, 1)
        xs.append(x[ok]), ys.append(y[ok]), ids.append(np.full(ok.sum(), k))
    x, y, ids = np.concatenate(xs), np.concatenate(ys), np.concatenate(ids)
    sel = np.random.default_rng(0).permutation(len(x))[:60000]
    x, y, ids = x[sel], y[sel], ids[sel]
    n = len(arws)
    th0 = np.log(np.diff(C.a_lineal(NODOS_G)) + 1e-4)
    M0 = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    p0 = np.r_[th0, M0.ravel(), np.zeros(n)]

    def res(p):
        g, M, lk = p[:24], p[24:33].reshape(3, 3), p[33:]
        pred = (_g(g, x) @ M.T) * np.exp(lk[ids])[:, None]
        suave = 0.5 * np.diff(g, 2)                                            # incrementos de g suaves: extrapola con sensatez fuera de los datos (x > 0,96)
        return np.r_[(np.log(np.maximum(pred, 1e-6)) - np.log(y)).ravel(), suave * np.sqrt(len(y))]
    r = least_squares(res, p0, loss="soft_l1", f_scale=0.05, max_nfev=400)
    g, M, lk = r.x[:24], r.x[24:33].reshape(3, 3), r.x[33:]
    s = 0.18 / float((_g(g, np.full((1, 3), GRIS_DISPLAY)) @ M.T)[0, 1])
    e = np.abs(r.fun[:3 * len(y)].reshape(-1, 3))
    return {"theta": g.tolist(), "M": (M * s).tolist(), "ganancias": {a.name: float(np.exp(-k) * s) for a, k in zip(arws, lk)},
            "error_log_medio": float(e.mean()), "error_log_p95": float(np.percentile(e, 95)), "muestras": int(len(x))}


def escena(ad: dict, x: np.ndarray) -> np.ndarray:
    """Display de la A6000 (0…1) → XYZ de escena (18 % gris → Y = 0,18)."""
    return _g(np.asarray(ad["theta"]), np.clip(x, 0, 1)) @ np.asarray(ad["M"]).T


# ---------- objetivos ----------
_INV = {}


def _inversa_s2v():
    """Inversa de `S1IIS2V` (STD de la S1II → V-Log): interpolación lineal sobre los 33³ nodos directos; fuera del casco, el vecino más cercano."""
    if "f" not in _INV:
        from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
        tab, lo, hi = C.lee_cube(DATOS / "S1IIS2V.cube")
        n = tab.shape[0]
        g = np.linspace(0, 1, n)
        std = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)
        v = C.aplica_cube(tab, lo, hi, std)
        lin, cer = LinearNDInterpolator(v, std), NearestNDInterpolator(v, std)
        _INV["f"] = lambda q: np.where(np.isnan(l := lin(q)), cer(q), l)
    return _INV["f"]


def objetivo(look: dict, ad: dict):
    """f(x) RGB de la A6000 [M,3] → RGB sRGB de la película."""
    if look["vlog"] is not None:
        tab, lo, hi = C.lee_cube(look["vlog"])
        return lambda x: np.clip(C.aplica_cube(tab, lo, hi, np.clip(vlog(escena(ad, x) @ XYZ_VGAMUT.T), 0, 1)), 0, 1)
    tab, lo, hi = C.lee_cube(look["std"])
    inv = _inversa_s2v()
    return lambda x: np.clip(C.aplica_cube(tab, lo, hi, np.clip(inv(np.clip(vlog(escena(ad, x) @ XYZ_VGAMUT.T), 0, 1)), 0, 1)), 0, 1)


def referencia(look: dict, xyz: np.ndarray):
    """La película aplicada a la escena del RAW (sin pasar por el render de la cámara)."""
    v = np.clip(vlog(xyz @ XYZ_VGAMUT.T), 0, 1)
    if look["vlog"] is not None:
        tab, lo, hi = C.lee_cube(look["vlog"])
        return np.clip(C.aplica_cube(tab, lo, hi, v), 0, 1)
    tab, lo, hi = C.lee_cube(look["std"])
    return np.clip(C.aplica_cube(tab, lo, hi, np.clip(_inversa_s2v()(v), 0, 1)), 0, 1)


# ---------- hardware ----------
def _con_t(f, T, foto=None) -> C.Cadena:
    """Cadena con la curva `T` dada (None = gamma sin tocar) y la LUT 5×9×9 ajustada en ΔE2000 por encima (como `descompone`)."""
    import lut_opt
    ch = C.Cadena(T=T)
    xt, w = lut_opt.muestras(foto=foto)
    ch.q = lut_opt.ajusta_de(ch.pre_lut(xt), f(xt), w, lut_opt.MODELO_DEFECTO)
    ch.rec = int(np.sum((ch.q == -64) | (ch.q == 63)))
    return ch


def t_grises(f):
    """T = respuesta del look sobre el eje neutro (media de canales), monótona: la curva tonal pasa a la etapa 1D y la LUT solo trata el color."""
    v = np.linspace(0, 1, 257)
    t = np.maximum.accumulate(f(np.repeat(v[:, None], 3, 1)).mean(1))
    return C.curva_tabla(lambda l: np.interp(C.de_lineal(l), v, t))


def ajusta_look(look: dict, ad: dict, foto: np.ndarray | None = None) -> dict:
    """T (1024 u16 sobre el código de gamma; None = sin curva) + q (405×3 s7). Tres candidatos (sin T, T del eje neutro, T por intervalos de
    `descompone`); gana el menor ΔE2000 medio, mitad sobre 20 000 colores al azar y mitad sobre píxeles reales de la A6000 (`foto`)."""
    f = objetivo(look, ad)
    x = np.random.default_rng(7).random((20000, 3))
    yt = f(x)
    yf = f(foto) if foto is not None else None
    mejor = None
    for nombre, ch in (("sin_T", _con_t(f, None, foto)), ("T_grises", _con_t(f, t_grises(f), foto)),
                       ("T_intervalos", C.descompone(f, usa_M=False, usa_T=True, usa_L=True, foto=foto))):
        e = C.de2000(yt, ch(x))
        ef = C.de2000(yf, ch(foto)) if foto is not None else e
        r = {"curva": nombre, "q": ch.q, "T": None if nombre == "sin_T" else tono_post.curva_post(ch),
             "de_medio": float(e.mean()), "de_p95": float(np.percentile(e, 95)), "de_max": float(e.max()), "de_fotos": float(ef.mean()),
             "nodos_al_tope": int(ch.rec)}
        r["criterio"] = (r["de_medio"] + r["de_fotos"]) / 2
        if mejor is None or r["criterio"] < mejor["criterio"]:
            mejor = r
    return mejor


def pixeles(arws: list[Path], n: int = 6000) -> np.ndarray:
    """Píxeles reales (JPEG embebido) de varias ARW: la distribución de color que la LUT verá en la cámara."""
    from PIL import Image
    import rawpy
    xs = []
    for a in arws:
        with rawpy.imread(str(a)) as r:
            im = Image.open(io.BytesIO(r.extract_thumb().data)).convert("RGB").reduce(8)
        xs.append(np.asarray(im, float).reshape(-1, 3) / 255)
    x = np.concatenate(xs)
    return x[np.random.default_rng(3).permutation(len(x))[:n]]


def aplica_hw(r: dict, x: np.ndarray) -> np.ndarray:
    """La cámara: T sobre el código de gamma (display) y después la LUT 5×9×9."""
    c = x if r["T"] is None else np.interp(np.clip(x, 0, 1) * 1023, np.arange(1024), r["T"] / 1023)
    return np.clip(C.aplica_lut3d(r["q"], c), 0, 1)


def _trabajo(args):
    look, ad, foto = args
    return look["id"], ajusta_look(look, ad, foto)


def prueba(looks: list[dict], res: dict, ad: dict, arw: Path, destino: Path) -> dict:
    """ΔE en la foto: adaptador (objetivo sobre el JPEG vs película sobre el RAW) y cámara (T+LUT sobre el JPEG vs película sobre el RAW); paneles."""
    from PIL import Image, ImageDraw
    x, xyz = par(arw, paso=4)
    xyz = xyz * ad["ganancias"].get(arw.name, _ganancia(ad, x, xyz))
    h, w = x.shape[:2]
    X, Z = x.reshape(-1, 3), xyz.reshape(-1, 3)
    out, tiras = {}, []
    for lk in looks:
        r = res[lk["id"]]
        ref = referencia(lk, Z)
        ideal = objetivo(lk, ad)(X)
        cam = aplica_hw(r, X)
        e_ad, e_cam = C.de2000(ref, ideal), C.de2000(ref, cam)
        e_hw = C.de2000(ideal, cam)
        out[lk["id"]] = {"de_hw_en_foto": round(float(e_hw.mean()), 2), "de_adaptador_medio": round(float(e_ad.mean()), 2), "de_camara_medio": round(float(e_cam.mean()), 2), "de_camara_p95": round(float(np.percentile(e_cam, 95)), 2)}
        fila = np.concatenate([x, ref.reshape(h, w, 3), cam.reshape(h, w, 3)], 1)
        im = Image.fromarray((np.clip(fila, 0, 1) * 255 + 0.5).astype(np.uint8))
        ImageDraw.Draw(im).text((6, 6), f"{lk['nombre']}  ΔE {out[lk['id']]['de_camara_medio']}", fill="white")
        tiras.append(im)
    for k in range(0, len(tiras), 6):
        grupo = tiras[k:k + 6]
        hoja = Image.new("RGB", (grupo[0].width, sum(t.height for t in grupo)))
        for j, t in enumerate(grupo):
            hoja.paste(t, (0, j * t.height))
        hoja.save(destino / f"prueba_{arw.stem}_{k // 6 + 1}.jpg", quality=88)
    return out


def _ganancia(ad: dict, x: np.ndarray, xyz: np.ndarray) -> float:
    """Ganancia de una foto que no entró en el ajuste: mediana del cociente escena/RAW en Y con píxeles no recortados."""
    ok = np.all((x > 0.05) & (x < 0.9), -1)
    return float(np.median(escena(ad, x[ok])[:, 1] / np.maximum(xyz[ok][:, 1], 1e-6)))


def guarda(salida: Path, looks: list[dict], res: dict) -> None:
    """`looks.npz` (q y T por look, orden del catálogo) e `informe.json`."""
    np.savez_compressed(salida / "looks.npz", ids=np.array([lk["id"] for lk in looks]), nombres=np.array([lk["nombre"] for lk in looks]),
                        q=np.stack([res[lk["id"]]["q"] for lk in looks]),
                        T=np.stack([res[lk["id"]]["T"] if res[lk["id"]]["T"] is not None else np.arange(1024, dtype=np.uint16) for lk in looks]),
                        curva=np.array([res[lk["id"]]["curva"] for lk in looks]))


def main(salida: Path, arw: Path | None, fotos: Path | None, solo: list[str] | None) -> dict:
    salida.mkdir(parents=True, exist_ok=True)
    looks = [lk for lk in catalogo() if not solo or lk["id"] in solo]
    fad = salida / "adaptador.json"
    if fad.exists():
        ad = json.loads(fad.read_text())
    else:
        ad = ajusta_adaptador(sorted((fotos or arw.parent).glob("*.ARW")))
        fad.write_text(json.dumps(ad, indent=1))
    foto = pixeles([a for a in sorted((fotos or arw.parent).glob("*.ARW")) if arw is None or a.name != arw.name])   # la foto de prueba no entra en el ajuste
    with ProcessPoolExecutor(8) as ex:
        res = dict(ex.map(_trabajo, [(lk, ad, foto) for lk in looks]))
    guarda(salida, looks, res)
    inf = {"adaptador": {k: ad[k] for k in ("error_log_medio", "error_log_p95", "muestras")}, "looks": {}}
    for lk in looks:
        r = res[lk["id"]]
        inf["looks"][lk["id"]] = {"nombre": lk["nombre"], "papel": lk["papel"], "curva": r["curva"], "de_medio": round(r["de_medio"], 3),
                                  "de_p95": round(r["de_p95"], 3), "de_max": round(r["de_max"], 2), "de_fotos": round(r["de_fotos"], 3), "nodos_al_tope": r["nodos_al_tope"]}
    if arw:
        for k, v in prueba(looks, res, ad, arw, salida).items():
            inf["looks"][k].update(v)
    (salida / "informe.json").write_text(json.dumps(inf, indent=1, ensure_ascii=False))
    return inf


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    op = lambda k: a[a.index(k) + 1] if k in a else None
    print(json.dumps(main(Path(a[0]), Path(op("--arw")) if op("--arw") else None, Path(op("--fotos")) if op("--fotos") else None,
                          op("--solo").split(",") if op("--solo") else None), indent=1, ensure_ascii=False))
