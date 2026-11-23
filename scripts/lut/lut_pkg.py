"""G95 (LUT-PKG-1) — LUT precalculada en el PC para que la cámara no procese nada: `LUT/LUT<n>.LUT` en la SD.

La tabla 5×9×9 se ajusta en el PC en ΔE2000 (`cube_a6000.descompone`, mejor que el muestreo del nodo que hace `lutsd.c` con un `.cube`)
y se guarda ya en el formato de la ranura del blob de Backup (405 nodos × 21 bits, orden lógico, `avcam_dinamico.empaqueta_21`).
El hilo de la SD (`lutsd.c`, `lutsd_paquete`) solo comprueba la cabecera y el CRC y copia los 1064 B; si falta o no vale, sigue con el `.cube`.
Formato v1 (1080 B, little-endian): `A6LT` (u32) · versión 1 (u8) · 0 (u8) · 1064 (u16) · CRC32 IEEE de la carga (u32) · 0 (u32) · carga 1064 B.
shortcut: solo la tabla; la curva T (LUT-T-1) entrará como versión 2 cuando exista su consumidor en `av-cam`.
`python3 lut_pkg.py ENTRADA.cube SALIDA.LUT` genera el fichero.
"""
from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
import avcam_dinamico as D
import cube_a6000 as C

MAGIC, VERSION, CARGA = 0x544C3641, 1, D.LUT_BYTES          # "A6LT"
TAM = 16 + CARGA


def paquete(carga: bytes) -> bytes:
    assert len(carga) == CARGA
    return struct.pack("<IBBHII", MAGIC, VERSION, 0, CARGA, zlib.crc32(carga), 0) + carga


def valida(b: bytes) -> bytes | None:
    """Referencia de `lutsd_paquete`: la carga si el fichero es un paquete v1 íntegro, si no None."""
    if len(b) != TAM:
        return None
    magic, ver, _, n, crc, _ = struct.unpack_from("<IBBHII", b)
    carga = b[16:]
    return carga if (magic, ver, n) == (MAGIC, VERSION, CARGA) and zlib.crc32(carga) == crc else None


def desde_funcion(f, img: bytes | None = None) -> bytes:
    """Ajuste en ΔE de la LUT 5×9×9 a `f` (RGB → RGB, [M,3] en 0…1) → paquete."""
    img = img if img is not None else C.BIN.read_bytes()
    hw = C.empaqueta_hw(C.descompone(f, usa_M=False, usa_T=False, usa_L=True).q, img)
    return paquete(D.empaqueta_21(hw, list(struct.unpack_from("<405H", img, D.PERM - D.BASE))))


def desde_cube(ruta: Path) -> bytes:
    tab, lo, hi = C.lee_cube(ruta)
    return desde_funcion(lambda x: C.aplica_cube(tab, lo, hi, x))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: lut_pkg.py ENTRADA.cube SALIDA.LUT")
    Path(sys.argv[2]).write_bytes(desde_cube(Path(sys.argv[1])))
