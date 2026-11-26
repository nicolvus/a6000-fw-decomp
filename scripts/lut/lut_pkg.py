"""G95/G115 (LUT-PKG-1) — LUT precalculada en el PC para que la cámara no procese nada: `LUT/LUT<n>.LUT` en la SD.

La tabla 5×9×9 se ajusta en el PC en ΔE2000 (`cube_a6000.descompone`, mejor que el muestreo del nodo que hace `lutsd.c` con un `.cube`)
y se guarda ya en el formato de la ranura del blob de Backup (405 nodos × 21 bits, orden lógico, `avcam_dinamico.empaqueta_21`).
El hilo de la SD (`lutsd.c`, `lutsd_paquete`) solo comprueba la cabecera y el CRC y copia; si falta o no vale, sigue con el `.cube`.

**Versión 1** (1080 B, little-endian): `A6LT` (u32) · versión 1 (u8) · 0 (u8) · 1064 (u16) · CRC32 IEEE de la carga (u32) · 0 (u32) · carga 1064 B.

**Versión 2** (LUT-T-1, 3128 B): igual, con versión 2, `usa_T` en el byte 5, el CRC sobre tabla+curva y 2048 B más de curva 1D:

| Desplazamiento | Campo |
|---|---|
| 0 | `A6LT` (u32) |
| 4 | versión 2 (u8) |
| 5 | `usa_T` (u8): 0 = la LUT no lleva curva, 1 = sí |
| 6 | 1064 (u16), longitud de la tabla (como en v1) |
| 8 | CRC32 IEEE de los 1064 + 2048 B siguientes |
| 12 | 0 (u32) |
| 16 | tabla: 405 nodos × 21 bits |
| 1080 | curva T: 1024 u16 sobre el código de gamma |

`usa_T = 0` guarda la curva igualmente (para no cambiar el tamaño con el flag): la cámara solo la usa si vale 1. La cámara la
guarda compacta en el blob (33 nodos cada 32 códigos, `lut_t.NN`/`REC`) y la expande en su cueva.
`python3 lut_pkg.py ENTRADA.cube SALIDA.LUT [--t|--sin-t]` genera el fichero (por defecto elige T por ΔE, ~1 min).
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
import avcam_dinamico as D
import cube_a6000 as C
import lut_t as TT

MAGIC, VERSION, CARGA = 0x544C3641, 2, D.LUT_BYTES          # "A6LT"
TAM_CURVA = 2048                                             # 1024 u16
TAM1, TAM2 = 16 + CARGA, 16 + CARGA + TAM_CURVA               # 1080 / 3128
TAM = TAM1                                                   # v1 (compatibilidad con G95); v2 en `TAM2`


def paquete(carga: bytes, t=None, usa_t: bool = True) -> bytes:
    """v1 si `t` es None; si no v2 con la curva de 1024 valores (lista, array o 2048 B) y el flag `usa_t`."""
    assert len(carga) == CARGA
    if t is None:
        return struct.pack("<IBBHII", MAGIC, 1, 0, CARGA, zlib.crc32(carga), 0) + carga
    t = np_u16(TT.curva_valores(t))
    assert len(t) == TAM_CURVA
    return struct.pack("<IBBHII", MAGIC, VERSION, 1 if usa_t else 0, CARGA, zlib.crc32(carga + t), 0) + carga + t


def np_u16(t) -> bytes:
    if isinstance(t, (bytes, bytearray)):
        assert len(t) == TAM_CURVA
        return bytes(t)
    return struct.pack("<1024H", *(int(v) for v in t))


def desempaqueta(b: bytes) -> tuple[bytes, bytes | None] | None:
    """Referencia de `lutsd_paquete`: (carga, curva|None) si el fichero es un paquete íntegro (v1 o v2), si no None."""
    if len(b) < 16:
        return None
    magic, ver, usa, n, crc, _ = struct.unpack_from("<IBBHII", b)
    if magic != MAGIC or n != CARGA:
        return None
    if ver == 1 and len(b) == TAM1:
        carga = b[16:]
        return (carga, None) if zlib.crc32(carga) == crc else None
    if ver == 2 and len(b) == TAM2:
        carga, t = b[16:16 + CARGA], b[16 + CARGA:]
        return (carga, t if usa else None) if zlib.crc32(carga + t) == crc else None
    return None


def valida(b: bytes) -> bytes | None:
    """Compatibilidad con G95: la carga si el paquete vale (v1 o v2), si no None."""
    r = desempaqueta(b)
    return r[0] if r else None


def curva(b: bytes) -> bytes | None:
    """Curva de 1024 u16 del paquete v2 (None en v1 o si `usa_T` = 0)."""
    r = desempaqueta(b)
    return r[1] if r else None


def registro(t) -> bytes:
    """Curva de 1024 → registro compacto de 68 B del blob (lo mismo que hace `lutsd_curva` en C)."""
    return TT.registro(None if t is None else TT.nodos(TT.curva_valores(t)))


def elige_t(f) -> bool:
    """¿Mejora la curva T a esta LUT? Ajusta la cadena con y sin T y compara ΔE2000 medio en 4000 colores uniformes."""
    x = np.random.default_rng(7).random((4000, 3))
    solo = C.descompone(f, usa_M=False, usa_T=False, usa_L=True)
    con = C.descompone(f, usa_M=False, usa_T=True, usa_L=True)
    return float(C.de2000(f(x), con(x)).mean()) < float(C.de2000(f(x), solo(x)).mean())


def desde_funcion(f, img: bytes | None = None, usa_t: bool | None = None) -> bytes:
    """Ajuste en ΔE de la LUT 5×9×9 a `f` (RGB → RGB, [M,3] en 0…1) → paquete. `usa_t=None`: lo elige por ΔE; False: v1 sin curva."""
    img = img if img is not None else C.BIN.read_bytes()
    usa_t = elige_t(f) if usa_t is None else usa_t
    ch = C.descompone(f, usa_M=False, usa_T=bool(usa_t), usa_L=True)
    hw = C.empaqueta_hw(ch.q, img)
    carga = D.empaqueta_21(hw, list(struct.unpack_from("<405H", img, D.PERM - D.BASE)))
    return paquete(carga, TT.curva_valores(curva_tono(ch)) if usa_t else None)


def curva_tono(ch) -> bytes:
    """1024 u16 (little-endian) de la curva T de una `cube_a6000.Cadena`."""
    import tono_post as P
    return np_u16(P.curva_post(ch))


def desde_cube(ruta: Path, usa_t: bool | None = None) -> bytes:
    tab, lo, hi = C.lee_cube(ruta)
    return desde_funcion(lambda x: C.aplica_cube(tab, lo, hi, x), usa_t=usa_t)


def main(argv: list[str]) -> None:
    if not 2 <= len(argv) <= 3:
        sys.exit("uso: lut_pkg.py ENTRADA.cube SALIDA.LUT [--t|--sin-t]")
    usa = None if len(argv) < 3 else {"--t": True, "--sin-t": False}[argv[2]]
    Path(argv[1]).write_bytes(desde_cube(Path(argv[0]), usa))


if __name__ == "__main__":
    main(sys.argv[1:])
