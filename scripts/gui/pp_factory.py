#!/usr/bin/env python3
"""G35 — valores de fábrica de los perfiles PP1…PP10 (y del bloque neutro «Off») que `Reset` restablece en la `libObj` de la A6000.

Una tabla de 11 perfiles × 31 parámetros en el dominio de la app (el mismo que guarda la NVRAM por perfil y que usa `pp_menu_spec`): índice de parámetro i = (clave − 0x1F8) / 4.
shortcut: los valores salen de la documentación de Sony (gamma y Color Mode por perfil, el resto neutro) recordada de memoria, NO de este firmware: la tabla real
vive en la NVRAM de fábrica de cada cámara. Se ajusta aquí sin tocar nada más.
"""
import struct

N_PARAMS, N_PERFILES = 31, 11                  # perfiles 0–8 = PP1–PP9, 9 = bloque neutro del selector «Off», 10 = PP10
GAMMA = dict(movie=4, still=5, itu709=3, cine1=6, cine2=7, itu709_800=10, slog2=11, slog3=2)
COLOR = dict(movie=5, still=6, cinema=7, pro=3, itu709=4, sgamut=9, sgamut3cine=11, sgamut3=10)
# índice → valor neutro (el 0 por omisión): nivel de Color Mode 4, Black Gamma Range Middle, sensibilidad Knee Mid, Max Point 4 (100 %, sin rodilla), Point 6 (90 %),
# B/W Balance Type3 (valor 2), Limit 7
NEUTRO = {1: 4, 8: 1, 12: 1, 13: 4, 14: 6, 19: 2, 20: 7}
I_COLOR, I_GAMMA = 0, 7
PERFILES = [   # (gamma, Color Mode)
    ("movie", "movie"), ("still", "still"), ("itu709", "itu709"), ("itu709_800", "itu709"), ("cine1", "cinema"), ("cine2", "cinema"),
    ("slog2", "sgamut"), ("slog2", "sgamut"), ("slog3", "sgamut3cine"),
    ("movie", "movie"),                                                  # 9 = «Off»: neutro
    ("slog3", "sgamut3"),                                                # 10 = PP10
]


def perfil(k: int) -> list[int]:
    v = [NEUTRO.get(i, 0) for i in range(N_PARAMS)]
    g, c = PERFILES[k]
    v[I_GAMMA], v[I_COLOR] = GAMMA[g], COLOR[c]
    return v


def tabla() -> bytes:
    """11 × 31 palabras de 32 bits (con signo), en el orden en que `Reset` indexa: (perfil·31 + i)·4."""
    return b"".join(struct.pack("<i", x) for k in range(N_PERFILES) for x in perfil(k))
