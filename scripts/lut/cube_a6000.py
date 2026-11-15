"""G71 — descompone un `.cube` (17³/33³/65³) en las etapas programables de la A6000 y mide el error.

Cadena modelada (la de la cámara, g71 §2): RGB de pantalla x → lineal (EOTF sRGB) → matriz 3×3 M (G27, 9 s16 Q10) → curva 1D COMPARTIDA T (G25/G67, 2048 u16)
→ YCbCr (BT.601, rango completo) → LUT 3D 5×9×9 de deltas s7 (`0x437a198c`) → salida.
shortcut: la gamma de la cámara es UNA tabla para los 3 canales (no por canal): las diferencias por canal van al residuo de la LUT 3D; rango de la LUT ±63 uds (ΔY ±24,6 %, ΔC ±36,9 % de medio rango), lo que se salga se recorta y se informa.
El orden respecto a gamma/matriz es el de la lógica del generador (la LUT trabaja en YCbCr, tras gamma); no medido en cámara.
uso: cube_a6000.py [--demo DIR] [--arw RAW] [fichero.cube …]
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE, PERM, N = 0x43541000, 0x43BEF2AC, 405
NY, NC = 5, 9
UY, UC = 1 / 256, 0.75 / 256                 # paso de 1 unidad s7: ΔY en 0..256; Δ croma = 0,75 códigos de ±128 (generador, g71 §1)
EJE_Y = np.linspace(0, 1, NY)                # 0, 64, …, 256 (/256)
EJE_C = np.linspace(-0.5, 0.5, NC)           # −128 … 128 paso 32 (/256)
N_CURVA, ESCALA_CURVA = 2048, 0.00271        # entrada lineal i·0,00271 → 10 bits (g67 §3)


# ---------- .cube ----------
def lee_cube(ruta: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """→ (tabla [n,n,n,3] con índice [r,g,b], dom_min, dom_max). Formato Adobe: el primer índice (R) varía más rápido."""
    n, lo, hi, filas = 0, np.zeros(3), np.ones(3), []
    for lin in Path(ruta).read_text().splitlines():
        t = lin.split("#")[0].split()
        if not t:
            continue
        if t[0] == "LUT_3D_SIZE":
            n = int(t[1])
        elif t[0] == "DOMAIN_MIN":
            lo = np.array(t[1:4], float)
        elif t[0] == "DOMAIN_MAX":
            hi = np.array(t[1:4], float)
        elif t[0] in ("TITLE", "LUT_1D_SIZE", "LUT_1D_INPUT_RANGE", "LUT_3D_INPUT_RANGE"):
            if t[0] == "LUT_1D_SIZE":
                raise ValueError("solo .cube 3D")
        else:
            filas.append([float(v) for v in t[:3]])
    if n < 2 or len(filas) != n ** 3:
        raise ValueError(f"cube inválido: n={n}, filas={len(filas)}")
    return np.array(filas).reshape(n, n, n, 3).transpose(2, 1, 0, 3), lo, hi      # [b,g,r]→[r,g,b]


def escribe_cube(ruta: Path, f, n: int, titulo: str) -> None:
    g = np.linspace(0, 1, n)
    r, gg, b = np.meshgrid(g, g, g, indexing="ij")
    v = np.clip(f(np.stack([r, gg, b], -1).reshape(-1, 3)), 0, 1).reshape(n, n, n, 3)
    filas = v.transpose(2, 1, 0, 3).reshape(-1, 3)
    Path(ruta).write_text(f'TITLE "{titulo}"\nLUT_3D_SIZE {n}\n' + "".join(f"{a:.6f} {b:.6f} {c:.6f}\n" for a, b, c in filas))


def aplica_cube(tab: np.ndarray, lo, hi, x: np.ndarray) -> np.ndarray:
    """Interpolación trilineal del .cube. x: [...,3] en el dominio."""
    n = tab.shape[0]
    u = np.clip((x - lo) / (hi - lo), 0, 1) * (n - 1)
    i0 = np.minimum(u.astype(int), n - 2)
    f = u - i0
    out = 0
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                w = (f[..., 0] if dr else 1 - f[..., 0]) * (f[..., 1] if dg else 1 - f[..., 1]) * (f[..., 2] if db else 1 - f[..., 2])
                out = out + w[..., None] * tab[i0[..., 0] + dr, i0[..., 1] + dg, i0[..., 2] + db]
    return out


# ---------- espacios ----------
def a_lineal(x):
    return np.where(x <= 0.04045, x / 12.92, ((np.clip(x, 0, None) + 0.055) / 1.055) ** 2.4)


def de_lineal(l):
    l = np.clip(l, 0, None)
    return np.where(l <= 0.0031308, 12.92 * l, 1.055 * l ** (1 / 2.4) - 0.055)


def rgb2ycc(c):
    y = c @ np.array([0.299, 0.587, 0.114])
    return np.stack([y, (c[..., 2] - y) / 1.772, (c[..., 0] - y) / 1.402], -1)


def ycc2rgb(t):
    y, cb, cr = t[..., 0], t[..., 1], t[..., 2]
    r = y + 1.402 * cr
    b = y + 1.772 * cb
    return np.stack([r, (y - 0.299 * r - 0.114 * b) / 0.587, b], -1)


def a_lab(rgb):
    l = a_lineal(np.clip(rgb, 0, 1))
    xyz = l @ np.array([[0.4124, 0.2126, 0.0193], [0.3576, 0.7152, 0.1192], [0.1805, 0.0722, 0.9505]]) / np.array([0.95047, 1, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def de2000(a, b):
    """ΔE CIEDE2000 entre dos arrays RGB sRGB [...,3] (0..1)."""
    L1, a1, b1 = np.moveaxis(a_lab(a), -1, 0)
    L2, a2, b2 = np.moveaxis(a_lab(b), -1, 0)
    C1, C2 = np.hypot(a1, b1), np.hypot(a2, b2)
    G = 0.5 * (1 - np.sqrt(((C1 + C2) / 2) ** 7 / (((C1 + C2) / 2) ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1, h2 = np.degrees(np.arctan2(b1, a1p)) % 360, np.degrees(np.arctan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2 - C1p
    dh = h2 - h1
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dh = np.where(C1p * C2p == 0, 0, dh)
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lm, Cm = (L1 + L2) / 2, (C1p + C2p) / 2
    hs = h1 + h2
    hm = np.where(np.abs(h1 - h2) > 180, (hs + 360) / 2 * (hs < 360) + (hs - 360) / 2 * (hs >= 360), hs / 2)
    hm = np.where(C1p * C2p == 0, hs, hm)
    T = 1 - 0.17 * np.cos(np.radians(hm - 30)) + 0.24 * np.cos(np.radians(2 * hm)) + 0.32 * np.cos(np.radians(3 * hm + 6)) - 0.20 * np.cos(np.radians(4 * hm - 63))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / np.sqrt(20 + (Lm - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cm, 1 + 0.015 * Cm * T
    Rt = -2 * np.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)) * np.sin(np.radians(60 * np.exp(-(((hm - 275) / 25) ** 2))))
    return np.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


# ---------- etapas ----------
def q10(m):
    return np.clip(np.round(m * 1024), -32768, 32767).astype(np.int16)


def curva_tabla(t_en_lineal) -> np.ndarray:
    """2048 u16 (código de 10 bits) a partir de T(lineal)∈[0,1]; entrada i·0,00271."""
    i = np.arange(N_CURVA) * ESCALA_CURVA
    return np.clip(np.round(t_en_lineal(i) * 1023), 0, 1023).astype(np.uint16)


def curva_aplica(tab: np.ndarray, m):
    return np.interp(np.clip(m, 0, None) / ESCALA_CURVA, np.arange(N_CURVA), tab / 1023.0)


def pesos(u: np.ndarray):
    """Pesos trilineales de [M,3] (Y,Cb,Cr) sobre los 405 nodos → (índices [M,8], pesos [M,8])."""
    gy = np.clip(u[:, 0], 0, 1) * (NY - 1)
    gb = (np.clip(u[:, 1], -0.5, 0.5) + 0.5) * (NC - 1)
    gr = (np.clip(u[:, 2], -0.5, 0.5) + 0.5) * (NC - 1)
    i0 = np.stack([np.minimum(gy.astype(int), NY - 2), np.minimum(gb.astype(int), NC - 2), np.minimum(gr.astype(int), NC - 2)], 1)
    f = np.stack([gy, gb, gr], 1) - i0
    idx, w = [], []
    for dy in (0, 1):
        for db in (0, 1):
            for dr in (0, 1):
                idx.append((i0[:, 0] + dy) * 81 + (i0[:, 1] + db) * 9 + i0[:, 2] + dr)
                w.append((f[:, 0] if dy else 1 - f[:, 0]) * (f[:, 1] if db else 1 - f[:, 1]) * (f[:, 2] if dr else 1 - f[:, 2]))
    return np.stack(idx, 1), np.stack(w, 1)


def ajusta_lut3d(u: np.ndarray, resid: np.ndarray, lam: float = 2e-3) -> np.ndarray:
    """Mínimos cuadrados de los deltas por nodo (405×3, en unidades normalizadas) con regularización de Laplaciano; sin recortar."""
    idx, w = pesos(u)
    A = np.zeros((N, N))
    rhs = np.zeros((N, 3))
    for k in range(8):
        np.add.at(rhs, idx[:, k], w[:, k, None] * resid)
        for k2 in range(8):
            np.add.at(A, (idx[:, k], idx[:, k2]), w[:, k] * w[:, k2])
    L = np.zeros((N, N))                                     # suavidad entre nodos vecinos + ancla débil a 0 en los nodos sin datos
    for j in range(NY):
        for a in range(NC):
            for b in range(NC):
                i = j * 81 + a * 9 + b
                for dj, da, db in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    if j + dj < NY and a + da < NC and b + db < NC:
                        k = i + dj * 81 + da * 9 + db
                        L[i, i] += 1; L[k, k] += 1; L[i, k] -= 1; L[k, i] -= 1
    s = len(u) / N
    A += s * lam * L + 1e-6 * s * np.eye(N)
    return np.linalg.solve(A, rhs)


def a_unidades(delta: np.ndarray) -> tuple[np.ndarray, int]:
    """Deltas normalizados → enteros s7 del hardware (ΔY en 1/256, ΔC en 0,75/256). Devuelve (int8 [405,3], nodos recortados)."""
    raw = np.round(delta / np.array([UY, UC, UC]))
    rec = int(np.sum(np.abs(raw) > 63 + 0.5))
    return np.clip(raw, -64, 63).astype(np.int8), rec


def empaqueta_hw(q: np.ndarray, img: bytes | None = None) -> bytes:
    """0x654 B en el orden del hardware: palabra `perm[i]` = (c0&0x7f)<<16 | (c1&0x7f)<<8 | (c2&0x7f) (empaquetador 0x437a198c)."""
    img = img if img is not None else BIN.read_bytes()
    perm = struct.unpack_from("<405H", img, PERM - BASE)
    out = bytearray(0x654)
    for i in range(N):
        c = q[i].astype(int) & 0x7F
        struct.pack_into("<I", out, 4 * perm[i], c[0] << 16 | c[1] << 8 | c[2])
    return bytes(out)


def aplica_lut3d(q: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Aplica la LUT cuantizada (trilineal) a colores c [M,3] RGB de pantalla (tras M y T) → RGB."""
    u = rgb2ycc(c)
    idx, w = pesos(u)
    d = (q.astype(float) * np.array([UY, UC, UC]))
    return ycc2rgb(u + np.einsum("mk,mkc->mc", w, d[idx]))


# ---------- descomposición ----------
class Cadena:
    def __init__(self, M=None, T=None, q=None):
        self.M = np.eye(3) if M is None else M
        self.T = curva_tabla(lambda l: de_lineal(l)) if T is None else T
        self.q = q

    def pre_lut(self, x):
        return curva_aplica(self.T, a_lineal(x) @ self.M.T)

    def __call__(self, x):
        c = self.pre_lut(x)
        return np.clip(c if self.q is None else aplica_lut3d(self.q, c), 0, 1)


def rejilla(n=21):
    g = np.linspace(0, 1, n)
    return np.stack(np.meshgrid(g, g, g, indexing="ij"), -1).reshape(-1, 3)


def descompone(f, usa_M=True, usa_T=True, usa_L=True, n=21) -> Cadena:
    """f: x[M,3] → RGB objetivo."""
    x = rejilla(n)
    y = f(x)
    lin = a_lineal(x)
    M = np.eye(3)
    if usa_M:
        M = np.linalg.lstsq(lin, a_lineal(np.clip(y, 0, 1)), rcond=None)[0].T
        M = q10(M).astype(float) / 1024
    T = None
    if usa_T:
        m = np.clip(lin @ M.T, 0, 1).ravel()
        v = y.ravel()
        b = np.minimum((m * 255).astype(int), 255)
        med = np.array([v[b == k].mean() if np.any(b == k) else np.nan for k in range(256)])
        cen = np.array([m[b == k].mean() if np.any(b == k) else np.nan for k in range(256)])
        ok = ~np.isnan(med)
        med = np.maximum.accumulate(med[ok])                  # monótona (suficiente: la tabla real exige no decreciente)
        T = curva_tabla(lambda i: np.interp(i, np.r_[0, cen[ok], 1], np.r_[med[0] if ok[0] else 0, med, med[-1]]))
    ch = Cadena(M, T)
    q = None
    if usa_L:
        u = rgb2ycc(ch.pre_lut(x))
        q, rec = a_unidades(ajusta_lut3d(u, rgb2ycc(y) - u))
        ch.rec = rec
    ch.q = q
    return ch


def error(f, ch: Cadena, x: np.ndarray) -> tuple[float, float, float]:
    e = de2000(f(x), ch(x))
    return float(e.mean()), float(np.percentile(e, 95)), float(e.max())


# ---------- LUT sintéticas ----------
def lut_identidad(x):
    return x


def lut_teal_orange(x):
    y = (x @ np.array([0.299, 0.587, 0.114]))[:, None]
    teal, orange = np.array([-0.05, 0.03, 0.06]), np.array([0.07, 0.02, -0.07])
    s = 1.12                                                 # algo más de saturación
    g = y + (x - y) * s
    return np.clip(g + (1 - y) ** 1.5 * teal + y ** 1.5 * orange, 0, 1)


def lut_pelicula(x):
    s = lambda v, k: 1 / (1 + np.exp(-k * (v - 0.5)))
    k = np.array([5.0, 5.4, 6.0])                           # curva S; el azul algo más dura (cruce)
    v = (s(x, k) - s(0, k)) / (s(1, k) - s(0, k))
    y = (v @ np.array([0.299, 0.587, 0.114]))[:, None]
    v = y + (v - y) * (1 - 0.35 * np.clip((y - 0.6) / 0.4, 0, 1))      # desatura altas luces
    return np.clip(v + (1 - y) * np.array([0.0, 0.015, 0.03]) * 1.5 + y * np.array([0.03, 0.01, -0.02]), 0, 1)


SINT = {"identidad": lut_identidad, "teal_orange": lut_teal_orange, "pelicula": lut_pelicula}


def foto(arw: Path, ancho=480) -> np.ndarray:
    import rawpy
    from PIL import Image
    with rawpy.imread(str(arw)) as r:
        rgb = r.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
    im = Image.fromarray(rgb)
    im = im.resize((ancho, int(im.height * ancho / im.width)))
    return np.asarray(im, float).reshape(-1, 3) / 255


COMBOS = {"nada": (0, 0, 0), "M": (1, 0, 0), "T": (0, 1, 0), "M+T": (1, 1, 0), "LUT": (0, 0, 1), "M+LUT": (1, 0, 1), "T+LUT": (0, 1, 1), "M+T+LUT": (1, 1, 1)}


def informe(f, x_den, x_img) -> dict:
    """Error de las 8 combinaciones de etapas ("nada" = cadena neutra de fábrica); la mejor por ΔE medio denso es la que usa `elige`."""
    res = {}
    for modo, fl in COMBOS.items():
        ch = Cadena() if not any(fl) else descompone(f, *map(bool, fl))
        res[modo] = (error(f, ch, x_den), error(f, ch, x_img) if x_img is not None else None, getattr(ch, "rec", 0), ch)
    return res


def elige(f, x_den) -> tuple[str, Cadena]:
    r = informe(f, x_den, None)
    m = min(r, key=lambda k: r[k][0][0])
    return m, r[m][3]


def panel(arw: Path, destino: Path, fn: dict) -> None:
    """Fila por LUT: original | .cube exacto | solo LUT 5×9×9 | cadena elegida (T+LUT…)."""
    import rawpy
    from PIL import Image
    with rawpy.imread(str(arw)) as r:
        rgb = r.postprocess(use_camera_wb=True, no_auto_bright=True, output_bps=8)
    im = Image.fromarray(rgb)
    im = im.resize((360, int(im.height * 360 / im.width)))
    x = np.asarray(im, float).reshape(-1, 3) / 255
    h, w = im.height, im.width
    filas = []
    for f in fn.values():
        _, ch = elige(f, np.random.default_rng(7).random((20000, 3)))
        solo = descompone(f, False, False, True)
        cols = [x, np.clip(f(x), 0, 1), solo(x), ch(x)]
        filas.append(np.concatenate([(c.reshape(h, w, 3) * 255).astype(np.uint8) for c in cols], 1))
    Image.fromarray(np.concatenate(filas, 0)).save(destino)


def main(args: list[str]) -> None:
    arw = Path(args[args.index("--arw") + 1]) if "--arw" in args else None
    destino = Path(args[args.index("--demo") + 1]) if "--demo" in args else None
    rng = np.random.default_rng(7)
    x_den = rng.random((30000, 3))
    x_img = foto(arw) if arw else None
    if destino:
        destino.mkdir(parents=True, exist_ok=True)
    if "--panel" in args and arw:
        panel(arw, Path(args[args.index("--panel") + 1]), {k: v for k, v in SINT.items() if k != "identidad"})
    for nombre, f in SINT.items():
        if destino:
            for n in (17, 33):
                escribe_cube(destino / f"{nombre}_{n}.cube", f, n, nombre)
            tab, lo, hi = lee_cube(destino / f"{nombre}_33.cube")
            f = lambda x, tab=tab, lo=lo, hi=hi: aplica_cube(tab, lo, hi, x)     # la cadena se ajusta al .cube leído, no a la fórmula
        print(f"== {nombre}")
        res = informe(f, x_den, x_img)
        mejor = min(res, key=lambda k: res[k][0][0])
        for modo, (den, img, rec, _) in res.items():
            print(("* " if modo == mejor else "  ") + f"{modo:8s} denso ΔE medio {den[0]:.2f} p95 {den[1]:.2f} máx {den[2]:.2f}" + (f" | foto medio {img[0]:.2f} p95 {img[1]:.2f}" if img else "") + (f" | nodos recortados {rec}" if rec else ""))


if __name__ == "__main__":
    main(sys.argv[1:])
