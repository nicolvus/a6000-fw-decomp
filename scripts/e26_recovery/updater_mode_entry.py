"""Añade `\\updater\\mode` (0 B) a una imagen FAT de `nflasha2` con el menor cambio posible y lo comprueba como Loader3.

Loader3 (`c01f159a` → `c01f44c6`) solo busca la entrada corta `MODE       ` en el primer clúster de
`\\updater`, sin LFN, con `attr & 0x18 == 0`, y no lee datos: basta una entrada de directorio.
Se escribe sin LFN y en mayúsculas para que el `rm -rf /setting/updater/mode*` de `execute_ufp.sh`
(glob sensible a mayúsculas) no la borre: persiste tras una sesión fallida y `CompleteUpdate` la
borra por API al terminar bien.  Si existe una entrada `MODE` borrada (0xE5) de 0 B, se recupera
cambiando un solo byte.  Nunca escribe en la cámara: lee y escribe archivos locales.

Uso: updater_mode_entry.py nflasha2.bin salida.bin
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

NAME = b"MODE       "
DELETED = b"\xe5ODE       "


def _geometry(img: bytes) -> tuple[int, int, int, int]:
    bps, spc, res, nfats, root_n, _tot, _media, spf = struct.unpack_from(
        "<HBHBHHBH", img, 11
    )
    root = (res + nfats * spf) * bps
    return root, root_n, root + root_n * 32, spc * bps


def updater_dir(img: bytes) -> tuple[int, int]:
    """(desplazamiento, tamaño) del primer clúster de `\\updater`, como lo lee Loader3."""
    root, root_n, data, cluster = _geometry(img)
    for i in range(root_n):
        e = img[root + 32 * i : root + 32 * i + 32]
        if e[:11] == b"UPDATER    " and e[11] & 0x18:
            return data + (struct.unpack_from("<H", e, 26)[0] - 2) * cluster, cluster
    raise ValueError("no hay directorio \\updater en la raíz")


def loader3_finds_mode(img: bytes) -> bool:
    """Réplica de `c01f3f34`: recorre hasta la primera entrada con nombre[0] == 0."""
    off, size = updater_dir(img)
    for j in range(size // 32):
        e = img[off + 32 * j : off + 32 * j + 32]
        if e[0] == 0:
            return False
        if e[:11] == NAME:
            return not e[11] & 0x18
    return False


def add_mode(img: bytes) -> tuple[bytes, list[dict]]:
    if loader3_finds_mode(img):
        raise ValueError("\\updater\\mode ya existe")
    off, size = updater_dir(img)
    out = bytearray(img)
    for j in range(size // 32):
        at = off + 32 * j
        e = img[at : at + 32]
        if e[:11] == DELETED and not e[11] & 0x18 and e[26:32] == bytes(6):
            out[at] = NAME[0]
            break
        if e[0] == 0:
            if j + 1 == size // 32:
                raise ValueError("sin hueco para el terminador en el primer clúster")
            out[at : at + 32] = NAME + b"\x20" + bytes(20)
            break
    else:
        raise ValueError("primer clúster de \\updater lleno")
    if not loader3_finds_mode(bytes(out)):
        raise AssertionError("Loader3 no encontraría la entrada escrita")
    changes = [
        {"offset": i, "sector": i // 512, "antes": img[i], "despues": out[i]}
        for i in range(off, off + size)
        if img[i] != out[i]
    ]
    return bytes(out), changes


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    out, changes = add_mode(src.read_bytes())
    dst.write_bytes(out)
    print(json.dumps(changes))


if __name__ == "__main__":
    main()
