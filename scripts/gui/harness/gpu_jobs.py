#!/usr/bin/env python3
"""Decodifica la tabla de trabajos y las listas de órdenes de la GPU de DMP volcadas con AREADUMP (G22 §5.18y).

uso: gpu_jobs.py DIR_TRABAJO   (lee area_dmpgles2_0.bin y area_stream_80000000.bin)

Tabla: ventana de /dev/dmpgles2, 0x320 entradas de 0x8c B desde +0xe8; palabra 4 = tipo (2 copia/subida de búfer,
3 sincronización, 6 copia a pantalla, 7 lista de dibujo), 18/19 = destino/origen (o lista), 20 = palabras de la lista.
Lista: pares (registro<<16 | máscara<<12 | extra, valor); con extra ≠ 0 siguen más valores consecutivos. Solo hay una
codificación medida (0x026 → índice + 4 flotantes en 0x450); las demás se tratan como un solo valor (sin verificar).
Fin de lista: registro 0x010 = 0x12345678.
"""
import struct
import sys
from pathlib import Path

TIPOS = {2: "copia", 3: "sync", 6: "pantalla", 7: "dibujo"}
GL_COMMON = 0x80000000
EXTRA = {0x026: 4}  # shortcut: solo la codificación medida; ampliar al ver otras en los volcados


def trabajos(win: bytes) -> list[tuple[int, tuple[int, ...]]]:
    out = []
    for k in range(0x320):
        o = 0xE8 + k * 0x8C
        if o + 0x8C > len(win):
            break
        e = struct.unpack_from("<35I", win, o)
        if any(e):
            out.append((k, e))
    return out


def decodifica_lista(mem: bytes, off: int, palabras: int) -> list[tuple[int, list[int]]]:
    """Devuelve [(registro, valores)]; las palabras que no son cabecera se devuelven con registro -1."""
    w = struct.unpack_from(f"<{palabras}I", mem, off)
    out, i = [], 0
    while i < len(w):
        h = w[i]
        reg, mask, extra = h >> 16, (h >> 12) & 0xF, h & 0xFFF
        if mask and reg < 0x800 and i + 1 < len(w):
            n = 1 + EXTRA.get(extra, 0)
            out.append((reg, list(w[i + 1:i + 1 + n])))
            i += 1 + n
            if reg == 0x010 and w[i - 1] == 0x12345678:
                break
        else:
            out.append((-1, [h]))
            i += 1
    return out


def main(work: Path) -> None:
    win = (work / "area_dmpgles2_0.bin").read_bytes()
    mem = (work / "area_stream_80000000.bin").read_bytes()
    for k, e in trabajos(win):
        print(f"#{k} tipo {e[4]} ({TIPOS.get(e[4], '?')}) dst={e[18]:#010x} src={e[19]:#010x} n={e[20]:#x}")
        if e[4] == 7 and GL_COMMON <= e[19] < GL_COMMON + len(mem):
            for reg, vals in decodifica_lista(mem, e[19] - GL_COMMON, e[20] * 2 or 0x100):
                print("   " + (f"{reg:03x}=" if reg >= 0 else "  ") + " ".join(f"{v:08x}" for v in vals))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
