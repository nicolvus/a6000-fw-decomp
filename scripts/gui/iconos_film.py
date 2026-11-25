#!/usr/bin/env python3
"""G110/G111 — Iconos propios del menú Fn para Film Simulation y Picture Profile: 70×60 con el dibujo (70×35) centrado, blancos con contorno oscuro.

G111 §15: el panel Fn dibuja la imagen de la propiedad 1 arriba de la casilla y centrada en horizontal; los ajustes nativos de icono simple
(Modo de medición, Efecto) usan 70×60 con el dibujo centrado (filas 11…48). El 70×35 del Estilo creativo deja hueco para «±0 ±0 ±0» y quedaba alto.

`python3 iconos_film.py` genera los PNG en `iconos/` (fuente Fira Sans Condensed Bold del sistema); la build solo lee los PNG, así que no depende de la fuente.
Film: marco de película (perforaciones arriba y abajo) con la abreviatura del look. PP: recuadro con «PP» y el número, u «OFF».
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DIR = Path(__file__).parent / "iconos"
W, H = 70, 35          # dibujo
ALTO = 60              # imagen final (casilla del panel Fn)
FUENTE = "/usr/share/fonts/TTF/FiraSansCondensed-Bold.ttf"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lut"))

# abreviatura de cada look en el orden de `film_userland.FILAS` (1…38); 0 = Off
ABREV = ("OFF",
         "E100", "EKTAR", "GOLD", "K64", "P160", "P400", "P800", "P800+1", "P800+2", "UMAX", "V200D", "V200T", "V250D", "V500T", "V50D",
         "C200", "400H", "RDP", "RVP", "XTRA", "ET250", "E250D", "ET400", "ET500", "EV160", "EV250", "EV500", "F64D", "R500D",
         "ASTIA", "CC", "CN", "ETERNA", "E-BB", "PRO N", "PROVIA", "REALA", "VELVIA")
PP = ("OFF",) + tuple(f"PP{k}" for k in range(1, 11))


def _texto(dr: ImageDraw.ImageDraw, caja: tuple[int, int, int, int], txt: str, tope: int) -> None:
    """`txt` centrado en `caja` con el mayor tamaño (≤ `tope`) que cabe."""
    x0, y0, x1, y1 = caja
    for t in range(tope, 6, -1):
        f = ImageFont.truetype(FUENTE, t)
        l, a, r, b = dr.textbbox((0, 0), txt, font=f)
        if r - l <= x1 - x0 and b - a <= y1 - y0:
            dr.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - a)) / 2 - a), txt, font=f, fill=255)
            return
    raise ValueError(txt)


def _rgba(mascara: Image.Image) -> np.ndarray:
    """Glifo blanco + contorno oscuro semitransparente de 1 px (como los iconos de Sony)."""
    m = np.asarray(mascara, np.float32) / 255
    borde = np.asarray(mascara.filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    a = np.maximum(m, borde * 0.6)
    gris = np.where(a > 0, m / np.maximum(a, 1e-6), 0)
    rgb = (40 + 215 * gris)[..., None].repeat(3, -1)
    return np.dstack([rgb, a * 255]).round().astype(np.uint8)


def _centra(dib: np.ndarray) -> np.ndarray:
    """Dibujo de 70×35 en una imagen de 70×60 transparente, centrado en vertical (como los iconos nativos de 70×60)."""
    out = np.zeros((ALTO, W, 4), np.uint8)
    y = (ALTO - H + 1) // 2
    out[y:y + H] = dib
    return out


def film(txt: str) -> np.ndarray:
    m = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(m)
    dr.rectangle((2, 2, W - 3, H - 3), outline=255, width=2)
    for x in range(6, W - 6, 8):                          # perforaciones
        dr.rectangle((x, 5, x + 3, 7), fill=255)
        dr.rectangle((x, H - 8, x + 3, H - 6), fill=255)
    _texto(dr, (6, 10, W - 6, H - 11), txt, 17)
    return _centra(_rgba(m))


def pp(txt: str) -> np.ndarray:
    m = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(m)
    dr.rounded_rectangle((6, 3, W - 7, H - 4), radius=4, outline=255, width=2)
    _texto(dr, (11, 7, W - 11, H - 8), txt if txt != "OFF" else "PP OFF", 20)
    return _centra(_rgba(m))


def carga() -> tuple[list[np.ndarray], list[np.ndarray]]:
    """(iconos Film 0…38, iconos PP Off, PP1…PP10) leídos de `iconos/`."""
    le = lambda n: np.asarray(Image.open(DIR / n).convert("RGBA"))
    return [le(f"film_{k:02d}.png") for k in range(len(ABREV))], [le(f"pp_{k:02d}.png") for k in range(len(PP))]


def main() -> None:
    import film_userland as FU
    assert len(ABREV) == 1 + sum(len(x) for _, x in FU.FILAS)
    DIR.mkdir(exist_ok=True)
    for k, t in enumerate(ABREV):
        Image.fromarray(film(t), "RGBA").save(DIR / f"film_{k:02d}.png")
    for k, t in enumerate(PP):
        Image.fromarray(pp(t), "RGBA").save(DIR / f"pp_{k:02d}.png")
    print(DIR, len(ABREV) + len(PP))


if __name__ == "__main__":
    main()
