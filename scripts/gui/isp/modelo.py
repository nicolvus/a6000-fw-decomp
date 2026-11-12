"""T9 — modelo por software (referencia en CPU/numpy) del pipeline de imagen de la BIONZ X con Picture Profile. El shader de `harness/isp_web.py` replica estas operaciones.

Cada etapa lleva su estado: REAL (dato leído de bytes del firmware/volcado), APROX (estructura razonable, constantes sin verificar) o NO_VERIFICADO.
Las constantes APROX están marcadas `shortcut:` y listadas en docs/gui/g23-isp-bionz-emulado.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

DIR = Path(__file__).resolve().parents[3] / "analysis/gui/isp"
N_LUT = 2048
N_PARAMS = 31

# índice de parámetro i (clave 0x1f8+4·i, G23/pp_menu_spec) → (id, etiqueta, mínimo, máximo); rangos = validador de la A6000 (REAL, G23)
PARAMS = {0: ("color_mode", "Color Mode", 3, 11), 1: ("color_level", "Color Mode Level", 1, 8), 7: ("gamma", "Gamma", 2, 11), 8: ("bg_range", "Black Gamma Range", 0, 2),
          9: ("bg_level", "Black Gamma Level", -7, 7), 10: ("black_level", "Black Level", -15, 15), 11: ("knee_mode", "Knee Mode", 0, 1),
          17: ("det_level", "Detail Level", -7, 7), 23: ("cd_r", "Color Depth R", -7, 7), 24: ("cd_g", "Color Depth G", -7, 7), 25: ("cd_b", "Color Depth B", -7, 7),
          26: ("cd_c", "Color Depth C", -7, 7), 27: ("cd_m", "Color Depth M", -7, 7), 28: ("cd_y", "Color Depth Y", -7, 7), 29: ("saturation", "Saturation", -8, 7),
          30: ("phase", "Color Phase", -7, 7)}
GAMMA_NOMBRES = {2: "S-Log3", 3: "ITU709", 4: "Movie", 5: "Still", 6: "Cine1", 7: "Cine2", 8: "Cine3", 9: "Cine4", 10: "ITU709(800%)", 11: "S-Log2"}
COLOR_NOMBRES = {3: "Pro", 4: "ITU709 Matrix", 5: "Movie", 6: "Still", 7: "Cinema", 8: "Black & White", 9: "S-Gamut", 10: "S-Gamut3", 11: "S-Gamut3.Cine"}
# Valor app de gamma → curva (selector = valor app, G25; A7S 0x43cab54d, A6000 0x43cb56e6 en blanco; Still en vídeo usa 0x0a como el CFW, G18)
CURVA_VIDEO = {2: "a6300_v1f", 3: "a7s_v16", 4: "a6000_v0a", 5: "a6000_v0a", 6: "a7s_v18", 7: "a7s_v19", 8: "a7s_v1a", 9: "a7s_v1b", 10: "a7s_v1c", 11: "a7s_v1d"}
CURVA_FOTO = {5: "a6000_f00"}   # Still en foto = gamma 0 (selector A7S 5 → (0,0)); el resto no tiene curva de foto propia: se usa la de vídeo (NO_VERIFICADO)
# Color Mode → índice de matriz de la propiedad 0x30001: solo Movie(0) está VERIFICADO (G27 §5); el resto es APROX (se deja Movie) hasta leer la tabla tipo→id→matriz de la A6000
MATRIZ_COLOR = {5: 0}
MATRIZ_DEFECTO = 0
# shortcut: pasos por unidad de los ajustes PP sin dato (el firmware lo guarda en tablas de hardware aún no localizadas); recalibrar con compara_real.py
PASO_BLACK, PASO_SAT, PASO_FASE_GRADOS, PASO_DEPTH = 0.002, 0.125, 2.0, 0.06   # Detail: solo en el shader (APROX)
NEUTRO = {"color_mode": 5, "gamma": 4, "black_level": 0, "saturation": 0, "phase": 0, "det_level": 0, "cd_r": 0, "cd_g": 0, "cd_b": 0, "cd_c": 0, "cd_m": 0, "cd_y": 0}
HUES = np.radians([0, 120, 240, 180, 300, 60])   # R G B C M Y sobre el plano Cb/Cr (BT.709 aprox.)
W709 = np.array([0.2126, 0.7152, 0.0722])


class Tablas:
    def __init__(self, dir_: Path = DIR) -> None:
        z = np.load(dir_ / "curvas.npz")
        self.curvas = {k: z[k] for k in z.files}
        self.meta = json.loads((dir_ / "tablas.json").read_text())
        self.matrices = np.array(self.meta["matrices_color"]["matrices"], float).reshape(-1, 3, 3) / 1024.0
        p = dir_ / "pp_ids.json"
        self.pp_ids = json.loads(p.read_text())["ids"] if p.is_file() else []

    def curva(self, gamma_app: int, foto: bool = False) -> tuple[str, np.ndarray]:
        k = CURVA_FOTO.get(gamma_app) if foto else None
        k = k or CURVA_VIDEO[gamma_app]
        return k, self.curvas[k].astype(float) / 1023.0


def srgb_a_lineal(v: np.ndarray) -> np.ndarray:   # APROX: el RAW del sensor no está disponible; la fuente se trata como sRGB
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def lut(c: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Curva de 2048 puntos con interpolación lineal; x en [0,1] (entrada lineal normalizada). Idéntico al shader (`texelFetch` + mix)."""
    f = np.clip(x, 0, 1) * (N_LUT - 1)
    i = np.minimum(f.astype(int), N_LUT - 2)
    t = f - i
    return c[i] * (1 - t) + c[i + 1] * t


def ganancia_filas(bandas: list | None, h: int) -> np.ndarray:
    """Ganancia vertical (h,) por interpolación lineal entre los centros de las bandas (arriba → abajo) del obturador medido; None = sin efecto."""
    if not bandas:
        return np.ones(h)
    b = np.array(bandas, float)
    return np.interp((np.arange(h) + 0.5) / h, (np.arange(len(b)) + 0.5) / len(b), b)


def aplica(rgb: np.ndarray, p: dict | None = None, t: Tablas | None = None, foto: bool = False, exposicion: float = 2.0,
           entrada_lineal: bool = False, bandas: list | None = None) -> np.ndarray:
    """rgb: float [0,1] (H,W,3) sRGB (o ya lineal con `entrada_lineal`, p. ej. un RAW con negro/WB aplicados) → salida [0,1] (códigos de la curva, recortados a 1).
    `bandas` = ganancia de exposición por bandas verticales (modo de obturador MEDIDO, ver g23 §6)."""
    t = t or Tablas()
    q = {**NEUTRO, **(p or {})}
    lin = (rgb if entrada_lineal else srgb_a_lineal(rgb)) * exposicion * ganancia_filas(bandas, rgb.shape[0])[:, None, None]                                      # exposición: APROX (nivel de entrada de la LUT sin verificar)
    lin = np.maximum(lin - q["black_level"] * PASO_BLACK, 0)                    # Black Level: APROX
    m = t.matrices[MATRIZ_COLOR.get(q["color_mode"], MATRIZ_DEFECTO)]           # matriz: REAL (valores); aplicada sobre sRGB lineal, no sobre RGB de sensor
    lin = np.maximum(lin @ m.T, 0)
    _, c = t.curva(q["gamma"], foto)
    y = lut(c, lin)                                                             # gamma por número: REAL
    luma = y @ W709
    cb, cr = (y[..., 2] - luma) / 1.8556, (y[..., 0] - luma) / 1.5748
    sat = max(0.0, 1 + q["saturation"] * PASO_SAT)                              # -8 = B&W (REAL, G27); escala APROX
    ang = np.radians(q["phase"] * PASO_FASE_GRADOS)
    cb, cr = cb * np.cos(ang) - cr * np.sin(ang), cb * np.sin(ang) + cr * np.cos(ang)
    h = np.arctan2(cr, cb)
    d = np.array([q[f"cd_{k}"] for k in "rgbcmy"], float) * PASO_DEPTH
    w = np.maximum(np.cos(h[..., None] - HUES), 0) ** 2                         # peso por tono: APROX
    g = sat * (1 + (w * d).sum(-1))
    cb, cr = cb * g, cr * g
    r_ = luma + 1.5748 * cr
    b_ = luma + 1.8556 * cb
    g_ = (luma - 0.2126 * r_ - 0.0722 * b_) / 0.7152
    out = np.stack([r_, g_, b_], -1)
    return np.clip(out, 0, 1)


def valor_a_bytes(v: int) -> bytes:
    """Elemento de Backup de PP: 1 byte (VERIFICADO, G36); los negativos como int8 complemento a dos (NO_VERIFICADO: no se ha visto un negativo en el volcado)."""
    return int(v).to_bytes(1, "little", signed=True)


def nvram_ops(t: Tablas, perfil: int, cambios: dict[str, int]) -> dict[int, bytes]:
    """{id de Backup: bytes} para escribir `cambios` ({id de ajuste: valor}) en el perfil 0–10; mismos ids que `libObj.so` (constructor 0x4a9a56)."""
    por_id = {v[0]: i for i, v in PARAMS.items()}
    out = {}
    for k, v in cambios.items():
        i = por_id[k]
        lo, hi = PARAMS[i][2:]
        if not lo <= v <= hi:
            raise ValueError(f"{k}={v} fuera de rango {lo}..{hi}")
        out[t.pp_ids[perfil][i]] = valor_a_bytes(v)
    return out


def ajustes_desde_nvram(t: Tablas, perfil: int, nv: dict[int, bytes]) -> dict[str, int]:
    """Valores del perfil presentes en `nv` (nvram.json de la emulación); lo que no está se omite (el volcado real de la A6000 no usa PP, G35)."""
    return {PARAMS[i][0]: int.from_bytes(nv[t.pp_ids[perfil][i]], "little", signed=True) for i in PARAMS if t.pp_ids[perfil][i] in nv}
