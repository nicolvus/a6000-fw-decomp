#!/usr/bin/env python3
"""G96 — seis películas analógicas icónicas ajustadas a la LUT 3D de la A6000 (paquetes `LUT/LUTn.LUT`, G95).

Cada película es un modelo paramétrico sobre la señal de pantalla de la cámara (sRGB, la misma suposición que `cube_a6000`):
1. color en YCbCr (el dominio del hardware): saturación global y por tono (rotación y ganancia con ventanas gaussianas en el ángulo Cb/Cr);
2. curva de tono por canal (S logística mezclada con la identidad; canales distintos = cruce de color);
3. virado de sombras y luces, negro levantado (fade) y blanco comprimido, desaturación de altas luces.
Los parámetros resumen descripciones publicadas (G96 §1); no son medidas de densitometría.
uso: peliculas.py SALIDA [--panel FOTO.JPG]  → SALIDA/LUT<n>.LUT, SALIDA/<nombre>.cube (33³, referencia) e informe.json
"""
from __future__ import annotations

import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import cube_a6000 as C
import lut_pkg as P

# ángulo atan2(Cr, Cb) en grados de los colores primarios en YCbCr 601 (pantalla)
TONO = {"rojo": 109, "piel": 123, "naranja": 140, "amarillo": 167, "verde": 225, "cian": 289, "azul": 349, "magenta": 61}


@dataclass
class Pelicula:
    nombre: str
    sat: float = 1.0                                           # saturación global
    tonos: dict = field(default_factory=dict)                  # tono → (rotación °, ganancia de croma)
    contraste: tuple = (0.0, 0.0, 0.0)                         # mezcla de la curva S por canal R, G, B (0 = lineal)
    pendiente: float = 6.0                                     # dureza de la S
    pivote: float = 0.5
    negro: tuple = (0.0, 0.0, 0.0)                             # negro levantado por canal (fade / dominante de sombras)
    blanco: tuple = (1.0, 1.0, 1.0)                            # blanco por canal (dominante de luces)
    sombra: tuple = (0.0, 0.0, 0.0)                            # virado RGB que pesa (1-Y)²
    luz: tuple = (0.0, 0.0, 0.0)                               # virado RGB que pesa Y²
    desat_luces: float = 0.0

    def __call__(self, x: np.ndarray) -> np.ndarray:
        x = np.clip(np.asarray(x, float), 0, 1)
        t = C.rgb2ycc(x)
        c = np.hypot(t[:, 1], t[:, 2])
        h = np.degrees(np.arctan2(t[:, 2], t[:, 1]))
        rot, gan = np.zeros_like(h), np.ones_like(h) * self.sat
        for nombre, (dh, g) in self.tonos.items():
            d = (h - TONO[nombre] + 180) % 360 - 180
            w = np.exp(-0.5 * (d / 28) ** 2)
            rot += w * dh
            gan *= 1 + w * (g - 1)
        h2 = np.radians(h + rot)
        c2 = c * gan
        v = C.ycc2rgb(np.stack([t[:, 0], c2 * np.cos(h2), c2 * np.sin(h2)], -1))
        s = lambda u, k: 1 / (1 + np.exp(-k * (u - self.pivote)))
        k = self.pendiente
        S = (s(np.clip(v, 0, 1), k) - s(0, k)) / (s(1, k) - s(0, k))
        a = np.asarray(self.contraste)
        v = (1 - a) * v + a * S
        y = (np.clip(v, 0, 1) @ np.array([0.299, 0.587, 0.114]))[:, None]
        if self.desat_luces:
            v = y + (v - y) * (1 - self.desat_luces * np.clip((y - 0.65) / 0.35, 0, 1))
        v = v + (1 - y) ** 2 * np.asarray(self.sombra) + y ** 2 * np.asarray(self.luz)
        n, b = np.asarray(self.negro), np.asarray(self.blanco)
        return np.clip(n + (b - n) * v, 0, 1)


# Orden = ranura de la SD (LUT1…LUT6).
PELICULAS = [
    # Kodachrome 64: rojos densos y algo cálidos, azules profundos, verdes y cian contenidos, contraste alto y sombras densas, ligera calidez.
    Pelicula("kodachrome64", sat=1.08, tonos={"rojo": (-3, 1.22), "naranja": (-2, 1.08), "amarillo": (-6, 1.05), "verde": (8, 0.82), "cian": (-10, 0.9), "azul": (8, 1.12)},
             contraste=(0.55, 0.55, 0.62), pendiente=6.0, pivote=0.48, negro=(0.0, 0.0, 0.01), blanco=(1.0, 0.985, 0.95), sombra=(0.0, -0.005, 0.0), luz=(0.015, 0.005, -0.02)),
    # Ektachrome E100: diapositiva limpia y neutra tirando a fría, saturación moderada, azules limpios, contraste medio-alto.
    Pelicula("ektachrome_e100", sat=1.12, tonos={"rojo": (0, 1.08), "magenta": (0, 1.08), "azul": (-4, 1.12), "cian": (-4, 1.08), "verde": (4, 1.0)},
             contraste=(0.42, 0.42, 0.45), pendiente=5.5, negro=(0.0, 0.0, 0.008), blanco=(0.985, 0.99, 1.0), sombra=(-0.006, 0.0, 0.012), luz=(-0.005, 0.0, 0.008)),
    # Velvia 50: saturación muy alta, azules y púrpuras ricos, verdes más cálidos, amarillos y naranjas intensos, contraste alto, sombras profundas.
    Pelicula("velvia50", sat=1.32, tonos={"azul": (6, 1.18), "magenta": (8, 1.15), "verde": (-10, 1.12), "amarillo": (-3, 1.15), "naranja": (-2, 1.1), "piel": (0, 0.95)},
             contraste=(0.6, 0.6, 0.66), pendiente=6.2, pivote=0.5, negro=(0.0, 0.0, 0.0), blanco=(1.0, 0.99, 0.98), sombra=(0.004, -0.008, 0.01), luz=(0.008, 0.0, -0.01)),
    # Portra 400: contraste bajo, sombras levantadas suaves, piel cálida sin ir a naranja, saturación contenida, verdes oliva, luces cremosas.
    Pelicula("portra400", sat=0.9, tonos={"piel": (2, 1.04), "rojo": (4, 0.92), "verde": (-8, 0.85), "cian": (0, 0.85), "azul": (-4, 0.9)},
             contraste=(0.12, 0.12, 0.08), pendiente=4.5, negro=(0.035, 0.03, 0.03), blanco=(0.985, 0.97, 0.94), sombra=(0.0, 0.006, 0.008), luz=(0.015, 0.008, -0.01), desat_luces=0.25),
    # Kodak Gold 200: cálida y amarilla, punch medio, amarillos y naranjas fuertes, azules algo apagados, sombras ligeramente levantadas.
    Pelicula("gold200", sat=1.1, tonos={"amarillo": (-4, 1.2), "naranja": (-3, 1.12), "rojo": (2, 1.05), "azul": (0, 0.9), "verde": (-6, 0.95)},
             contraste=(0.32, 0.3, 0.26), pendiente=5.0, negro=(0.025, 0.018, 0.01), blanco=(1.0, 0.975, 0.9), sombra=(0.006, 0.004, -0.006), luz=(0.02, 0.01, -0.025), desat_luces=0.15),
    # Fuji Pro 400H: paleta fría, verdes hacia cian, piel neutra con un punto rosado, sombras pastel levantadas, contraste bajo.
    Pelicula("pro400h", sat=0.92, tonos={"verde": (14, 0.95), "cian": (0, 0.92), "piel": (-4, 0.97), "rojo": (-4, 0.95), "azul": (-4, 0.95)},
             contraste=(0.1, 0.12, 0.1), pendiente=4.5, negro=(0.03, 0.04, 0.045), blanco=(0.975, 0.99, 0.99), sombra=(-0.006, 0.006, 0.01), luz=(0.0, 0.004, 0.006), desat_luces=0.2),
]


def ajusta(p: Pelicula, img: bytes):
    q = C.descompone(p, usa_M=False, usa_T=False, usa_L=True).q
    ch = C.Cadena(q=q)
    x = np.random.default_rng(7).random((20000, 3))
    e = C.de2000(p(x), ch(x))
    tope = int(np.sum((q == -64) | (q == 63)))
    return q, ch, {"de_medio": round(float(e.mean()), 3), "de_p95": round(float(np.percentile(e, 95)), 3), "de_max": round(float(e.max()), 2), "nodos_al_tope": tope}


def panel(foto: Path, destino: Path, filas: list) -> None:
    from PIL import Image, ImageDraw
    im = Image.open(foto).convert("RGB")
    im = im.resize((360, int(im.height * 360 / im.width)))
    u, v = np.meshgrid(np.linspace(0, 1, 360), np.linspace(1, 0, 60))     # carta: tono × luminosidad + rampa de grises
    carta = np.clip(C.ycc2rgb(np.stack([0.15 + 0.7 * v, 0.22 * np.cos(2 * np.pi * u), 0.22 * np.sin(2 * np.pi * u)], -1)), 0, 1)
    carta = np.concatenate([carta, np.repeat(np.linspace(0, 1, 360)[None, :, None], 3, 2).repeat(16, 0)])
    a = np.concatenate([np.asarray(im, float) / 255, carta]).reshape(-1, 3)
    w, h = 360, im.height + carta.shape[0]
    out = Image.new("RGB", (w * 3, h * len(filas)), "white")
    for i, (p, ch) in enumerate(filas):
        for j, img in enumerate((a, p(a), ch(a))):
            out.paste(Image.fromarray((np.clip(img, 0, 1).reshape(h, w, 3) * 255 + 0.5).astype(np.uint8)), (j * w, i * h))
        ImageDraw.Draw(out).text((4, i * h + 4), p.nombre, fill="white")
    out.save(destino)


def main(salida: Path, foto: Path | None = None) -> dict:
    salida.mkdir(parents=True, exist_ok=True)
    img = C.BIN.read_bytes()
    informe, filas = {}, []
    for n, p in enumerate(PELICULAS, 1):
        q, ch, inf = ajusta(p, img)
        carga = P.D.empaqueta_21(C.empaqueta_hw(q, img), list(struct.unpack_from("<405H", img, P.D.PERM - P.D.BASE)))
        (salida / f"LUT{n}.LUT").write_bytes(P.paquete(carga))
        C.escribe_cube(salida / f"{p.nombre}.cube", p, 33, p.nombre)
        informe[f"LUT{n}"] = {"pelicula": p.nombre, **inf}
        filas.append((p, ch))
    (salida / "informe.json").write_text(json.dumps(informe, indent=1))
    if foto:
        panel(foto, salida / "panel.png", filas)
    return informe


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit("uso: peliculas.py SALIDA [--panel FOTO.JPG]")
    print(json.dumps(main(Path(a[0]), Path(a[a.index("--panel") + 1]) if "--panel" in a else None), indent=1))
