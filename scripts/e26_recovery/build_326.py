"""Paquete de recuperación 3.26: el contenido oficial del 3.24 (tar y updater.img de Sony 3.21) con versión 3.26.

Tras instalar el 3.25, el actualizador solo acepta versiones > 3.25 y el 3.24 queda inútil.  En
lugar de reempaquetar 200 MB, se cambia el byte de versión de la cabecera FDAT, su CRC, la suma
del primer bloque de 1024 B y su cifrado (los 512 B iniciales van con una sola pasada AES), y el
CRC DEND del `.dat`.  Después se descifra el `.dat` completo y se compara con el FDAT plano.
Salida (no versionada): analysis/darwin-patch/fdat/recuperacion-326/.  Nunca instala nada.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from e25_06 import audit_packages as A  # type: ignore[import-not-found]

SRC = ROOT / "analysis/darwin-patch/fdat/recuperacion-324"
OUT = ROOT / "analysis/darwin-patch/fdat/recuperacion-326"
SRC_DAT_SHA = "e1345aff44270270fec8ae15014f3696cf98c06a07b9eaeb89ff6346e77c8f22"
SRC_FDAT_SHA = "24ee9b42e9fae29c7a86ec5f17d85d9a5076a8a36698a3766e0b13801126b2c2"
OFFICIAL_TAR_SHA = "970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8"
OFFICIAL_UPDATER_SHA = (
    "b6d5175245c8fb26879c5376f0e6e0d9ff13064f805d591954ff2a48a8c2566c"
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bump(
    dat: bytes, fdat: bytes, minor: int, keys: tuple[bytes, bytes]
) -> tuple[bytes, bytes]:
    """Devuelve (dat, fdat) con `versionMinor` = `minor` y todas las sumas recalculadas."""
    new_fdat = bytearray(fdat)
    new_fdat[32] = minor
    struct.pack_into("<I", new_fdat, 8, zlib.crc32(new_fdat[12 : A.FDAT_HDR]))

    info = A.parse_dat(dat)
    off = info["fdat_offset"]
    d1 = Cipher(algorithms.AES(keys[0]), modes.ECB()).decryptor()
    d2 = Cipher(algorithms.AES(keys[1]), modes.ECB()).decryptor()
    p1 = d1.update(dat[off : off + A.BLOCK])
    block = bytearray(p1[:512] + d2.update(p1)[512:])
    if bytes(block[4 : 4 + A.BLOCK - 4]) != fdat[: A.BLOCK - 4]:
        raise ValueError("el primer bloque descifrado no coincide con el FDAT plano")
    block[4 : 4 + A.BLOCK - 4] = new_fdat[: A.BLOCK - 4]
    struct.pack_into(
        "<H", block, 0, sum(struct.unpack_from("<511H", block, 2)) & 0xFFFF
    )
    e1 = Cipher(algorithms.AES(keys[0]), modes.ECB()).encryptor()
    e2 = Cipher(algorithms.AES(keys[1]), modes.ECB()).encryptor()
    enc = e1.update(bytes(block[:512])) + e1.update(e2.update(bytes(block[512:])))

    new_dat = bytearray(dat)
    new_dat[off : off + A.BLOCK] = enc
    dend = next(o for t, o, _ in info["chunks"] if t == "DEND")
    struct.pack_into(">I", new_dat, dend, zlib.crc32(new_dat[: dend - 8]))
    return bytes(new_dat), bytes(new_fdat)


def verify(dat: bytes, fdat: bytes, keys: tuple[bytes, bytes], version: str) -> dict:
    info = A.parse_dat(dat)
    res = A.decrypt_fdat(
        dat, info["fdat_offset"], info["fdat_size"], keys, compare=fdat
    )
    hdr = A.parse_fdat_header(fdat[: A.FDAT_HDR])
    tarbuf = memoryview(fdat)[
        hdr["firmware_offset"] : hdr["firmware_offset"] + hdr["firmware_size"]
    ]
    tar = A.parse_tar(tarbuf)
    upd = next(fs for fs in hdr["filesystems"] if fs["mode"] == "U")
    return {
        "dend_ok": info["dend_stored"] == info["dend_computed"],
        "descifrado_igual_a_fdat": res.first_mismatch_vs_fdat is None,
        "bloques_sin_error": not (res.bad_sum or res.bad_flag or res.bad_len),
        "crc_cabecera_ok": hdr["checksum_stored"] == hdr["checksum_computed"],
        "version": hdr["version"] == version,
        "modelo_region": (hdr["model"], hdr["region"]) == (0x41030035, 0),
        "tar_oficial": sha(bytes(tarbuf)) == OFFICIAL_TAR_SHA and not tar["problems"],
        "updater_oficial": sha(fdat[upd["offset"] : upd["offset"] + upd["size"]])
        == OFFICIAL_UPDATER_SHA,
    }


def main() -> None:
    dat, fdat = (
        (SRC / "firmware_packed.dat").read_bytes(),
        (SRC / "firmware_packed.fdat").read_bytes(),
    )
    if (sha(dat), sha(fdat)) != (SRC_DAT_SHA, SRC_FDAT_SHA):
        raise SystemExit("el paquete 3.24 de partida no es el verificado en E25-05")
    keys = A.load_keys()
    base = verify(dat, fdat, keys, "3.24")
    new_dat, new_fdat = bump(dat, fdat, 0x26, keys)
    checks = verify(new_dat, new_fdat, keys, "3.26")
    fdat_diff = [i for i in range(A.BLOCK) if fdat[i] != new_fdat[i]]
    dat_diff = A.diff_ranges(dat, new_dat)
    result = {
        "base_3_24": base,
        "comprobaciones_3_26": checks,
        "bytes_fdat_distintos": fdat_diff,
        "rangos_dat_distintos": dat_diff,
        "sha256": {"dat": sha(new_dat), "fdat": sha(new_fdat)},
    }
    if (
        not all(base.values())
        or not all(checks.values())
        or fdat_diff != [8, 9, 10, 11, 32]
    ):
        raise SystemExit(json.dumps(result, indent=1))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "firmware_packed.dat").write_bytes(new_dat)
    (OUT / "firmware_packed.fdat").write_bytes(new_fdat)
    (OUT / "SHA256SUMS").write_text(
        f"{sha(new_dat)}  firmware_packed.dat\n{sha(new_fdat)}  firmware_packed.fdat\n",
        encoding="utf-8",
    )
    manifest = ROOT / "analysis/e26-recovery/manifest-recuperacion-326.json"
    manifest.write_text(
        json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
