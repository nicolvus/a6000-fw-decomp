"""T9 — entrada RAW de la A6000 para el modelo del ISP: parámetros de revelado que la propia cámara guarda en el ARW (SR2Private cifrado), demosaico real y alineación geométrica con la vista previa de la BIONZ X.

Evidencia (g23 §4):
  * SR2Private (IFD `0xc634` → `0x7200` offset, `0x7201` longitud, `0x7221` clave): cifrado de Sony (`sony_decrypt` de dcraw: LFSR de 127 palabras, `pad[p]=pad[p+1]^pad[p+65]`). Descifrado correcto = el IFD interior
    se lee entero (209 etiquetas) y los datos tienen sentido: `0x7310` negro 512 ×4, `0x7313` WB RGGB (3148, 1024, 1024, 1644)/1024, `0x7800` matriz 3×3 (filas suman 1024) y `0x7802` curva de tono de 512 puntos (10 bit).
  * `0x7800` = byte a byte la matriz de Backup `0x30001` índices 0/2/5–8 (`tablas.json`): la matriz de color del estilo Standard es esa (REAL).
  * La vista previa (1616×1080) es el fotograma completo de 6024×4024 con **corrección de lente** (distorsión de barril; las líneas rectas del ARW salen curvas): el modelo no puede compararse píxel a píxel
    sin alinear. La corrección es radial `s = f·(1 + k1·r² + k2·r⁴)` + traslación; se ajusta por foto maximizando la correlación de gradientes (MEDIDO). T9-E: los parámetros de la lente SÍ están en el IFD del RAW (`0x7032/0x7035/0x7037`, no en SR2) y `carga` los usa (`lente_arw`).
Requiere numpy, rawpy, Pillow, opencv-python-headless y scipy (`.venv`).
"""
from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import numpy as np

TAM = (1616, 1080)   # vista previa de la A6000
BLANCO = 16383
DIR = Path(__file__).resolve().parents[3] / "analysis/gui/isp"
GEOMETRIA = DIR / "geometria_arw.json"
_M = 0xFFFFFFFF


def descifra_sony(datos: bytes, clave: int) -> bytes:
    pad = [0] * 128
    for p in range(4):
        clave = (clave * 48828125 + 1) & _M
        pad[p] = clave
    pad[3] = ((pad[3] << 1) & _M) | ((pad[0] ^ pad[2]) >> 31)
    for p in range(4, 127):
        pad[p] = (((pad[p - 4] ^ pad[p - 2]) << 1) & _M) | ((pad[p - 3] ^ pad[p - 1]) >> 31)
    pad = [int.from_bytes(x.to_bytes(4, "big"), "little") for x in pad]   # htonl en máquina LE
    n = len(datos) // 4
    w = list(struct.unpack(f"<{n}I", datos[:n * 4]))
    for i in range(n):
        p = (127 + i) & 127
        pad[p] = pad[(p + 1) & 127] ^ pad[(p + 65) & 127]
        w[i] ^= pad[p]
    return struct.pack(f"<{n}I", *w)


def sr2(b: bytes) -> dict[int, np.ndarray]:
    """Etiquetas del IFD SR2 descifrado de un ARW (bytes del fichero) → {etiqueta: array}."""
    def ifd(buf: bytes, o: int) -> dict:
        n = struct.unpack_from("<H", buf, o)[0]
        return {t: (ty, c, v, o + 2 + 12 * i) for i in range(n) for t, ty, c, v in [struct.unpack_from("<HHII", buf, o + 2 + 12 * i)]}
    sp = ifd(b, ifd(b, struct.unpack_from("<I", b, 4)[0])[0xC634][2])
    o, ln, clave = sp[0x7200][2], sp[0x7201][2], struct.unpack_from("<I", b, sp[0x7221][3] + 8)[0]
    d = descifra_sony(b[o:o + ln], clave)
    tam = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4}
    fmt = {1: "B", 2: "B", 3: "H", 4: "I", 5: "Q", 6: "b", 7: "B", 8: "h", 9: "i"}
    out = {}
    for t, (ty, c, v, _) in ifd(d, 0).items():
        s = tam[ty] * c
        raw = struct.pack("<I", v) if s <= 4 else d[v - o:v - o + s]   # los desplazamientos son del fichero
        out[t] = np.array(struct.unpack(f"<{c}{fmt[ty]}", raw[:s]))
    return out


def mapas(p: np.ndarray, W: int, H: int, w: int, h: int) -> tuple[np.ndarray, np.ndarray]:
    """Coordenadas (en la imagen W×H) de cada píxel de la vista previa w×h con p = (k1, k2, escala, dx, dy)."""
    xs, ys = (np.arange(w) + 0.5) / w * 2 - 1, ((np.arange(h) + 0.5) / h * 2 - 1) * (h / w)
    X, Y = np.meshgrid(xs, ys)
    r2 = X * X + Y * Y
    f = p[2] * (1 + p[0] * r2 + p[1] * r2 * r2)
    return ((X * f + p[3] + 1) / 2 * W - 0.5).astype(np.float32), ((((Y * f + p[4]) * (w / h)) + 1) / 2 * H - 0.5).astype(np.float32)


# Desplazamiento fijo del centro óptico respecto del RAW (MEDIDO: mediana de 32 ajustes por foto, desviación 2·10⁻⁴/4·10⁻⁴, ≈ 3 px de la vista previa).
DX_LENTE, DY_LENTE = -0.00407, 0.000185
# Escala: la vista previa conserva el aumento medio de la corrección: f = K·c(r)/media(c) (MEDIDO en 32 ARW de 4 focales, K = 0,9919 ± 0,0018; el escalado de Sony NO_VERIFICADO).
K_LENTE = 0.99194


def lente_arw(b: bytes) -> dict | None:
    """Parámetros de corrección de lente del IFD del RAW (SubIFD 0x14a; REAL): `0x7037` distorsión, `0x7035` aberración cromática (R y B), `0x7032` viñeteo; int16 con n nodos.
    None si el ARW no los trae."""
    def ifd(o: int) -> list[tuple[int, int, int, int]]:
        n = struct.unpack_from("<H", b, o)[0]
        return [struct.unpack_from("<HHII", b, o + 2 + 12 * i) for i in range(n)]
    sub = [v for t, _, c, v in ifd(struct.unpack_from("<I", b, 4)[0]) if t == 0x14A]
    if not sub:
        return None
    tg = {t: np.array(struct.unpack_from(f"<{c}h", b, v), float) for t, ty, c, v in ifd(sub[0]) if t in (0x7032, 0x7035, 0x7037) and ty == 8}
    if len(tg) < 3:
        return None
    d, ca, vg = tg[0x7037], tg[0x7035], tg[0x7032]
    n, nc = int(d[0]), int(ca[0]) // 2
    return {"dist": d[1:1 + n], "ca_r": ca[1:1 + nc], "ca_b": ca[1 + nc:1 + 2 * nc], "vig": vg[1:1 + int(vg[0])]}


def factor_lente(L: dict, rd: np.ndarray, canal: int) -> np.ndarray:
    """Radio fuente / radio destino en función del radio normalizado a la semidiagonal: 1 + dist·2⁻¹⁴, por (1 + ca·2⁻²¹) en R/B. Escalas y nodos
    equiespaciados como darktable/RawTherapee (shortcut: escala NO_VERIFICADA en el firmware; la valida el ajuste por foto, < 0,5 px de media)."""
    f = 1 + L["dist"] / 16384
    if canal != 1:
        f = f * (1 + L["ca_r" if canal == 0 else "ca_b"] / 2097152)
    return np.interp(rd, np.linspace(0, 1, len(f)), f)


def ganancia_vineteo(L: dict, rd: np.ndarray) -> np.ndarray:
    """1/caída de luz, caída = 2^(0,5 − 2^(v·2⁻¹³ − 1)) (darktable). La vista previa de la A6000 NO la aplica (MEDIDO, g23 §4.3): solo informativa."""
    v = 2 ** (0.5 - 2 ** (L["vig"] / 8192 - 1))
    return np.interp(rd, np.linspace(0, 1, len(v)), 1 / v)


def mapas_lente(L: dict, W: int, H: int, w: int, h: int, canal: int, dx: float = DX_LENTE, dy: float = DY_LENTE) -> tuple[np.ndarray, np.ndarray]:
    """Como `mapas`, pero con el factor radial de los parámetros del ARW en vez del ajuste por foto."""
    xs, ys = (np.arange(w) + 0.5) / w * 2 - 1, ((np.arange(h) + 0.5) / h * 2 - 1) * (h / w)
    X, Y = np.meshgrid(xs, ys)
    rd = np.hypot(X, Y) / np.hypot(1, h / w)
    f = factor_lente(L, rd, canal) * K_LENTE / factor_lente(L, rd, 1).mean()
    return ((X * f + dx + 1) / 2 * W - 0.5).astype(np.float32), ((((Y * f + dy) * (w / h)) + 1) / 2 * H - 0.5).astype(np.float32)


def alinea_lente(a: np.ndarray, L: dict, w: int = TAM[0], h: int = TAM[1]) -> np.ndarray:
    import cv2
    src = np.ascontiguousarray(a, np.float32)
    return np.stack([cv2.remap(np.ascontiguousarray(src[..., c]), *mapas_lente(L, a.shape[1], a.shape[0], w, h, c), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                     for c in range(3)], -1)


def alinea(a: np.ndarray, p: np.ndarray, w: int = TAM[0], h: int = TAM[1]) -> np.ndarray:
    import cv2
    sx, sy = mapas(p, a.shape[1], a.shape[0], w, h)
    return cv2.remap(np.ascontiguousarray(a, np.float32), sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def ajusta_geometria(lin: np.ndarray, prev: np.ndarray, w: int = 404, h: int = 270) -> tuple[np.ndarray, float]:
    """Parámetros (k1, k2, escala, dx, dy) y correlación de gradientes entre `lin` (RGB lineal a resolución ≥ 2·w) y la vista previa (RGB 0-1)."""
    import cv2
    from scipy.optimize import minimize

    def grad(g: np.ndarray) -> np.ndarray:
        g = cv2.GaussianBlur(g, (0, 0), 1.2)
        m = np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
        return m / (cv2.GaussianBlur(m, (0, 0), 20) + 1e-3)
    gc = grad(cv2.resize(cv2.cvtColor((np.clip(lin * 4, 0, 1) ** 0.5).astype(np.float32), cv2.COLOR_RGB2GRAY), (w * 2, h * 2), interpolation=cv2.INTER_AREA))
    gt = grad(cv2.resize(cv2.cvtColor(prev.astype(np.float32), cv2.COLOR_RGB2GRAY), (w, h), interpolation=cv2.INTER_AREA))
    coste = lambda p: -np.corrcoef(alinea(gc, p, w, h).ravel(), gt.ravel())[0, 1]
    p = np.array([min((-0.1, 0, 0.1, 0.2), key=lambda k: coste(np.array([k, 0, 1, 0, 0.]))), 0, 1, 0, 0.])
    for _ in range(3):
        r = minimize(coste, p, method="Powell", options={"xtol": 1e-4, "ftol": 1e-6, "maxiter": 2000})
        p = r.x
    return p, float(-r.fun)


def demosaico(raw: np.ndarray, bl: np.ndarray, wb: np.ndarray) -> np.ndarray:
    """Mosaico RGGB (uint16, sin recortar) → RGB lineal normalizado (negro restado, ganancias de WB as-shot, blanco 16383), demosaico de OpenCV 'edge-aware'."""
    import cv2
    m = raw.astype(np.float32)
    m[0::2, 0::2] -= bl[0]; m[0::2, 1::2] -= bl[1]; m[1::2, 0::2] -= bl[2]; m[1::2, 1::2] -= bl[3]
    m[0::2, 0::2] *= wb[0]; m[1::2, 1::2] *= wb[3]                               # WB RGGB: R = wb[0], G = 1, B = wb[3]
    m = np.clip(m / (BLANCO - bl.max()), 0, 4)
    # OpenCV nombra el patrón por la 2.ª fila/columna: RGGB → COLOR_BayerBG2RGB (verificado en test: R/G > 1 en el cielo, B/G < 1 en el ladrillo)
    return cv2.cvtColor(np.clip(m * 16383, 0, 65535).astype(np.uint16), cv2.COLOR_BayerBG2RGB_EA).astype(np.float32) / 16383


def carga(ruta: Path, geometria: dict | None = None) -> dict:
    """ARW → {lin: RGB lineal alineado a la vista previa (1616×1080), prev: vista previa 0-1, sr2: parámetros, geo: (k1,k2,esc,dx,dy), cc: calidad, meta}."""
    import cv2
    import rawpy
    from PIL import Image
    b = ruta.read_bytes()
    s = sr2(b)
    with rawpy.imread(str(ruta)) as r:
        raw = r.raw_image.copy()
        prev = np.asarray(Image.open(io.BytesIO(r.extract_thumb().data)).convert("RGB"), np.float32) / 255
    bl = s[0x7310].astype(np.float32)
    wb = s[0x7313].astype(np.float32) / 1024
    rgb = demosaico(raw, bl, wb)
    grande = cv2.resize(rgb, (TAM[0] * 2, TAM[1] * 2), interpolation=cv2.INTER_AREA)
    geo = (geometria or json.loads(GEOMETRIA.read_text() if GEOMETRIA.is_file() else "{}")).get(ruta.stem)
    L = lente_arw(b)
    if geo is None and L is not None:   # foto nueva: parámetros de lente del propio ARW (T9-E, ~0,9 px); el ajuste guardado se prefiere porque alinea mejor los bordes (g23 §4.3)
        return {"lin": alinea_lente(grande, L), "prev": prev, "sr2": s, "geo": None, "lente": L, "cc": float("nan")}
    if geo is None:
        p, cc = ajusta_geometria(grande, prev)
    else:
        p, cc = np.array(geo["p"]), geo["cc"]
    return {"lin": alinea(grande, p), "prev": prev, "sr2": s, "geo": p, "cc": cc}


def extrae_standard(arws: list[Path], salida: Path = DIR / "sr2_standard.json") -> dict:
    """Curva (512) y matriz SR2 de los ARW dados (Creative Style Standard); exige que sean idénticas en todos. Escribe `sr2_standard.json`."""
    ref = None
    for f in arws:
        s = sr2(f.read_bytes())
        k = (s[0x7802].tolist(), s[0x7800].tolist(), s[0x7310].tolist())
        assert ref is None or k == ref, f"{f.name} difiere"
        ref = k
    r = {"origen": f"SR2Private 0x7802/0x7800/0x7310 de {len(arws)} ARW de la A6000 (Creative Style Standard, DRO Auto), idénticos entre sí; ver g23 §4",
         "curva_0x7802": ref[0], "matriz_0x7800": ref[1], "escala_matriz": 1024, "negro_0x7310": ref[2]}
    salida.write_text(json.dumps(r, separators=(",", ":")))
    return r


if __name__ == "__main__":
    import sys
    fs = [Path(a) for a in sys.argv[1:]]
    r = extrae_standard(fs)
    print(f"{len(fs)} ARW idénticos; curva {len(r['curva_0x7802'])} pt, matriz {r['matriz_0x7800']}, negro {r['negro_0x7310']}")
