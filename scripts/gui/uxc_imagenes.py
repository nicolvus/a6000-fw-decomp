"""G110 — Imágenes de `image_*.uxc` (A6000 3.21): leer, codificar y añadir iconos propios.

Formato (VERIFICADO: las 38 de `image_Fn_Menu_169.uxc` y las 658+4 de `image_cmn_169.uxc` con tamaño de salida exacto se decodifican):
  * cabecera 16 B; cuenta de ranuras = u32 +12 & 0x1fff; id de la ranura i = primer id + i (0xc000 en `image_cmn`, deducido de cualquier registro); tabla u16 por ranura (índice en palabras desde
    `base` = 0x10 + 2·cuenta, 0xffff = vacía); registro de 20 B en `base + 4·t`: u16 id, u16 0x1a05, u32 formato (0xc0…), u16 ancho, u16 alto,
    u32 tamaño, u32 desplazamiento. Los de formato 0xc8… miden 40 B y no apuntan a datos.
  * **Los datos están en `base + 4·t + 4 + desplazamiento`**: relativo al propio registro (G104 lo tomaba relativo a `base + 4` y solo acertaba con el
    primero; por eso sus iconos ISO no salían).
  * Datos = registros LZPT (`0xF0` LZ77 / `0x0F` almacenado, los del LDEC por hardware, `/dev/ldec`) de ≤ 4096 B de salida; salida = RGBA4444 (u16 LE,
    R en los 4 bits altos). Formato `0xc0…` (las 5 947 de `image_cmn_169`): filas lineales de ancho redondeado a 16. Formato `0xe0…` (las 38 de
    `image_Fn_Menu_169`, las de la A7S): mosaico Morton 8×8 con ancho y alto redondeados a 8.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from e25_27 import tpzl

VACIA, REG, SELLO, FORMATO = 0xFFFF, 20, 0x1A05, 0xC000_0000
RES_IMAGEN = 0x0205_0000


def _indice(d: bytes) -> tuple[int, int, int, list[int]]:
    n = struct.unpack_from("<I", d, 12)[0] & 0x1FFF
    base, tab = 0x10 + 2 * n, list(struct.unpack_from(f"<{n}H", d, 0x10))
    i = next(i for i, t in enumerate(tab) if t != VACIA)
    return n, base, struct.unpack_from("<H", d, base + 4 * tab[i])[0] - i, tab


def inflate(s: bytes) -> bytes:
    """Registros LZPT seguidos hasta el primero que no es `0xF0`/`0x0F` (relleno)."""
    out, i = bytearray(), 0
    while i < len(s) and s[i] in (0xF0, 0x0F):
        seg, i = tpzl._inflate_segment(s, i)
        out += seg
    return bytes(out)


def morton(w: int, h: int) -> np.ndarray:
    """Desplazamiento en píxeles de (y, x) en una textura en mosaico 8×8 de Morton (`gpu_raster.tile_index`)."""
    y, x = np.mgrid[0:h, 0:w]
    m = (x & 1) | (y & 1) << 1 | (x & 2) << 1 | (y & 2) << 2 | (x & 4) << 2 | (y & 4) << 3
    return ((y >> 3) * (w >> 3) + (x >> 3)) * 64 + m


def registros(d: bytes) -> dict[int, tuple[tuple, int]]:
    """{id: (registro, posición de los datos)} de las imágenes con datos."""
    _, base, _, tab = _indice(d)
    out = {}
    for t in tab:
        if t == VACIA:
            continue
        r = struct.unpack_from("<HHIHHII", d, base + 4 * t)
        if r[2] >> 24 in (0xC0, 0xE0):
            out[r[0]] = (r, base + 4 * t + 4 + r[6])
    return out


def decodifica(d: bytes, rid: int) -> np.ndarray:
    """RGBA u8 (alto, ancho, 4) de la imagen `rid`."""
    r, p = registros(d)[rid]
    w, h = r[3], r[4]
    px = np.frombuffer(inflate(d[p:p + r[5]]), "<u2")
    if r[2] >> 24 == 0xE0:
        w8, h8 = (w + 7) // 8 * 8, (h + 7) // 8 * 8
        assert len(px) == w8 * h8, (hex(rid), len(px), w8, h8)
        v = px[morton(w8, h8)][:h, :w]
    else:
        w16 = (w + 15) // 16 * 16
        assert len(px) == w16 * h, (hex(rid), len(px), w16, h)
        v = px.reshape(h, w16)[:, :w]
    return np.stack([(v >> s) & 15 for s in (12, 8, 4, 0)], -1).astype(np.uint8) * 17


def codifica(rgba: np.ndarray) -> bytes:
    """RGBA u8 (alto, ancho, 4) → datos LZPT del formato `0xc0` (filas de ancho redondeado a 16; registros LZ77 de 4096 B de salida, como Sony)."""
    h, w = rgba.shape[:2]
    a = np.zeros((h, (w + 15) // 16 * 16, 4), np.uint16)
    a[:, :w] = (rgba.astype(np.uint16) + 8) // 17
    raw = (a[..., 0] << 12 | a[..., 1] << 8 | a[..., 2] << 4 | a[..., 3]).astype("<u2").tobytes()
    return b"".join(tpzl.encode_lz(raw[i:i + tpzl.RECORD]) for i in range(0, len(raw), tpzl.RECORD))


def anade(d: bytes, imagenes: list[np.ndarray], ocupadas=frozenset()) -> tuple[bytes, list[int]]:
    """Añade `imagenes` (RGBA) en ranuras libres (de la última hacia atrás, fuera de `ocupadas`). Devuelve (fichero, [id de cada imagen]).

    Los registros nuevos van tras el último registro y los datos se desplazan `hueco` B: cada registro con datos suma `hueco` a su desplazamiento
    (es relativo a su propia posición). Los datos nuevos van al final, alineados a 16 B."""
    n, base, primero, tab = _indice(d)
    libres = [primero + i for i in range(n - 1, -1, -1) if tab[i] == VACIA and primero + i not in ocupadas]
    assert len(libres) >= len(imagenes), "no hay ranuras libres"
    regs = [(t, struct.unpack_from("<HHIHHII", d, base + 4 * t)) for t in tab if t != VACIA]
    fin_regs = max(4 * t + (2 * REG if r[2] >> 24 == 0xC8 else REG) for t, r in regs)
    inicio_datos = min(4 * t + 4 + r[6] for t, r in regs if r[2] >> 24 in (0xC0, 0xE0))
    assert inicio_datos == fin_regs, (hex(inicio_datos), hex(fin_regs))
    hueco = (REG * len(imagenes) + 15) // 16 * 16
    assert (fin_regs + hueco) // 4 <= 0xFFFF
    out = bytearray(d[:base + fin_regs])
    for t, r in regs:
        if r[2] >> 24 in (0xC0, 0xE0):
            struct.pack_into("<I", out, base + 4 * t + 16, r[6] + hueco)
    cola = bytearray(d[base + fin_regs:])
    cola += b"\0" * (-len(cola) % 16)
    extra, ids = bytearray(), []
    for k, (img, rid) in enumerate(zip(imagenes, libres)):
        datos = codifica(img)
        t = (fin_regs + REG * k) // 4
        pos = fin_regs + hueco + len(cola) + len(extra)          # relativa a `base`
        out += struct.pack("<HHIHHII", rid, SELLO, FORMATO, img.shape[1], img.shape[0], len(datos), pos - 4 * t - 4)
        struct.pack_into("<H", out, 0x10 + 2 * (rid - primero), t)
        extra += datos + b"\0" * (-len(datos) % 16)
        ids.append(rid)
    out += b"\0" * (hueco - REG * len(imagenes))
    return bytes(out + cola + extra), ids
