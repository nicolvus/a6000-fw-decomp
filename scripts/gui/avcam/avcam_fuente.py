#!/usr/bin/env python3
"""Origen del av-cam que carga la LIRO VM: el mismo artefacto que se instalaría (E2E-1).

`.dat` (descifrado de emu_config) → tar `firmware` → `0700_part_image/dev/nflasha3` (TPZL) → FAT16 → `AV-CAM.BIN`. Acepta también el tar o el `nflasha3` crudo.
Uso: avcam_fuente.py RUTA [SALIDA]  (imprime sha256; con SALIDA escribe el av-cam)
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for p in (ROOT / "scripts", ROOT / "scripts/gui/harness"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from e25_27 import build, fatimg, tarball, tpzl

TAM = 11_427_236  # AV-CAM.BIN de toda versión (los parches no cambian el tamaño)


def _tar_de_dat(dat: bytes) -> bytes:
    import emu_config as E
    A = E._audit()
    fdat = E.descifra(dat, A)
    h = A.parse_fdat_header(fdat[:E.FDAT_HDR])
    return fdat[h["firmware_offset"]:h["firmware_offset"] + h["firmware_size"]]


def avcam_de(origen: Path) -> bytes:
    """Bytes de AV-CAM.BIN de un `.dat`, un tar de firmware o un `nflasha3` (TPZL); valida tamaño, `LIRO` y versión 4."""
    datos = Path(origen).read_bytes()
    if datos[:4] != b"TPZL" and datos[:5] != b"ustar" and datos[257:262] != b"ustar":  # ni TPZL ni tar: se intenta como .dat
        datos = _tar_de_dat(datos)
    if datos[257:262] == b"ustar":
        miembros = {e.name: e.data for e in tarball.parse(datos)[0]}
        if build.NFLASHA3 not in miembros:
            raise ValueError(f"el tar no contiene {build.NFLASHA3}")
        datos = miembros[build.NFLASHA3]
    # workers=1: con el pool por defecto falla fuera de `if __name__ == "__main__"`
    img = fatimg.Fat16.parse(tpzl.TpzlImage.parse(datos).decompressed(1)).read(build.AVCAM_NAME)
    if len(img) != TAM or img[4:8] != b"ORIL" or struct.unpack_from("<I", img, 8)[0] != 4:
        raise ValueError("AV-CAM.BIN con tamaño o cabecera LIRO inesperados")
    return img


def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


if __name__ == "__main__":
    b = avcam_de(Path(sys.argv[1]))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_bytes(b)
    print(sha(b))
