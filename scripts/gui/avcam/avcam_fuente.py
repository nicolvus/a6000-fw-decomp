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

_u16 = lambda b, o: struct.unpack_from("<H", b, o)[0]

TAM = 11_427_236  # AV-CAM.BIN de toda versión (los parches no cambian el tamaño)


def _tar_de_dat(dat: bytes) -> bytes:
    import emu_config as E
    A = E._audit()
    fdat = E.descifra(dat, A)
    h = A.parse_fdat_header(fdat[:E.FDAT_HDR])
    return fdat[h["firmware_offset"]:h["firmware_offset"] + h["firmware_size"]]


def _fat(origen: Path) -> fatimg.Fat16:
    datos = Path(origen).read_bytes()
    if datos[:4] != b"TPZL" and datos[:5] != b"ustar" and datos[257:262] != b"ustar":  # ni TPZL ni tar: se intenta como .dat
        datos = _tar_de_dat(datos)
    if datos[257:262] == b"ustar":
        miembros = {e.name: e.data for e in tarball.parse(datos)[0]}
        if build.NFLASHA3 not in miembros:
            raise ValueError(f"el tar no contiene {build.NFLASHA3}")
        datos = miembros[build.NFLASHA3]
    # workers=1: con el pool por defecto falla fuera de `if __name__ == "__main__"`
    return fatimg.Fat16.parse(tpzl.TpzlImage.parse(datos).decompressed(1))


def avcam_de(origen: Path) -> bytes:
    """Bytes de AV-CAM.BIN de un `.dat`, un tar de firmware o un `nflasha3` (TPZL); valida tamaño, `LIRO` y versión 4."""
    img = _fat(origen).read(build.AVCAM_NAME)
    if len(img) != TAM or img[4:8] != b"ORIL" or struct.unpack_from("<I", img, 8)[0] != 4:
        raise ValueError("AV-CAM.BIN con tamaño o cabecera LIRO inesperados")
    return img


def idt_de(origen: Path) -> bytes:
    """Bytes de `SABIN/IDT_CAM.BIN` (microcódigo del módulo IDT) del mismo nflasha3; `fatimg` solo lee la raíz, aquí se baja un nivel."""
    fat = _fat(origen)
    d = next(e for e in fat._entries() if fat._decode_name(e) == "SABIN" and e[11] & 0x10)
    c, buf = _u16(d, 26), bytearray()
    while 2 <= c < fat._eoc:
        o = fat.cluster_offset(c)
        buf += fat.data[o:o + fat.cluster_size]
        c = fat._fat_entry(c)
    for o in range(0, len(buf), 32):
        e = bytes(buf[o:o + 32])
        if e[0] == 0:
            break
        if e[0] != 0xE5 and fat._decode_name(e) == "IDT_CAM.BIN":
            size, out, c = struct.unpack_from("<I", e, 28)[0], bytearray(), _u16(e, 26)
            while 2 <= c < fat._eoc and len(out) < size:
                q = fat.cluster_offset(c)
                out += fat.data[q:q + fat.cluster_size]
                c = fat._fat_entry(c)
            return bytes(out[:size])
    raise ValueError("SABIN/IDT_CAM.BIN no encontrado")


def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


if __name__ == "__main__":
    b = avcam_de(Path(sys.argv[1]))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_bytes(b)
    print(sha(b))
