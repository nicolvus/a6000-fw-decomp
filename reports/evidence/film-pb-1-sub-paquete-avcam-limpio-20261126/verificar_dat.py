#!/usr/bin/env python3
"""FILM-PB-1 (26-11) — verificación de extremo a extremo sobre el `.dat` del paquete 3.94 (contenedor cifrado).

Descifra el `.dat` con el auditor del contenedor (`e25_06.audit_packages`, el mismo camino que
`audit_package_nflasha15.py`, no `fwtool`), escribe el `firmware.tar` que se instalaría y comprueba:
  * `AV-CAM.BIN` leído de vuelta == av-cam de fábrica 3.21, byte a byte;
  * `part_image.sum` válida;
  * el tar del `.dat` es el mismo que el construido en disco (`build/cfw_avcam_limpio/pkg-3.94/firmware.tar`);
  * respecto al `.dat` instalado (3.93), solo cambian `nflasha3` y su línea de suma.
Uso: verificar_dat.py DAT [--instalado TAR_393] → JSON a stdout. NO instala nada.
"""
import argparse
import hashlib
import json
import mmap
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/fwtool"))
from e25_06 import audit_packages as A
from e25_27 import build, fatimg, sums, tarball, tpzl

N3 = build.NFLASHA3
FABRICA = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
CHUNK = 1 << 20
TAR_EN_DISCO = ROOT / "build/cfw_avcam_limpio/pkg-3.94/firmware.tar"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def miembros(ruta: Path):
    """(nombre, cabecera, desplazamiento de datos, tamaño, SHA-256) de cada miembro, con mmap."""
    with open(ruta, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        pos = 0
        while pos + 512 <= len(mm):
            cab = mm[pos:pos + 512]
            if cab == b"\0" * 512:
                break
            nombre = cab[:100].split(b"\0", 1)[0].decode("utf-8", "replace")
            tam = tarball._parse_number(cab[124:136])
            h = hashlib.sha256()
            for k in range(pos + 512, pos + 512 + tam, CHUNK):
                h.update(mm[k:min(k + CHUNK, pos + 512 + tam)])
            yield nombre, cab, pos + 512, tam, h.hexdigest()
            pos += 512 + ((tam + 511) // 512) * 512


def main(dat: Path, instalado: Path) -> dict:
    blob = dat.read_bytes()
    dat_sha = sha(blob)
    info = A.parse_dat(blob)
    fdat = dat.with_suffix(".fdat").read_bytes()
    dec = A.decrypt_fdat(blob, info["fdat_offset"], info["fdat_size"], A.load_keys(), compare=fdat)
    hdr = A.parse_fdat_header(fdat[: A.FDAT_HDR])
    tar = fdat[hdr["firmware_offset"]:hdr["firmware_offset"] + hdr["firmware_size"]]
    fabrica = FABRICA.read_bytes()
    with tempfile.TemporaryDirectory() as t:
        ruta = Path(t) / "firmware.tar"
        ruta.write_bytes(tar)
        ent = {e[0]: e for e in miembros(ruta)}
        n3_off, n3_tam = ent[N3][2], ent[N3][3]
        with open(ruta, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            n3 = mm[n3_off:n3_off + n3_tam]
            sum_txt = mm[ent[build.PART_SUM][2]:ent[build.PART_SUM][2] + ent[build.PART_SUM][3]].decode("ascii")
        avcam = fatimg.Fat16.parse(tpzl.TpzlImage.parse(n3).decompressed(workers=1)).read(build.AVCAM_NAME)
    del blob
    propio = list(miembros(TAR_EN_DISCO))
    inst = list(miembros(instalado))
    cambios = [{"miembro": a[0], "bytes_antes": a[3], "bytes_despues": b[3], "sha256_antes": a[4], "sha256_despues": b[4]}
               for a, b in zip(inst, propio) if a[4] != b[4] or a[1] != b[1]]
    return {
        "dat": str(dat), "dat_sha256": dat_sha, "version": hdr.get("version"),
        "contenedor": {"dend_ok": info["dend_stored"] == info["dend_computed"],
                       "descifrado_igual_a_fdat": dec.first_mismatch_vs_fdat is None},
        "tar_del_dat": {"bytes": len(tar), "sha256": sha(tar), "miembros": len(propio),
                        "igual_al_tar_en_disco": [(a[0], a[4]) for a in propio] == [(b[0], b[4]) for b in
                                                                                    miembros(TAR_EN_DISCO)]},
        "avcam": {"bytes": len(avcam), "sha256": sha(avcam), "igual_al_de_fabrica": avcam == fabrica,
                  "fabrica_sha256": sha(fabrica)},
        "part_image_sum_valida": sums.verify(sum_txt, build.PART_ENTRY, n3),
        "nflasha3": {"bytes": len(n3), "sha256": sha(n3)},
        "vs_instalado": {"miembros_antes": len(inst), "miembros_despues": len(propio), "cambiados": cambios,
                         "quitados": sorted({a[0] for a in inst} - {b[0] for b in propio}),
                         "anadidos": sorted({b[0] for b in propio} - {a[0] for a in inst})},
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dat", type=Path)
    ap.add_argument("--instalado", type=Path, default=ROOT / "build/cfw_func393/pp/pkg-3.93/firmware.tar")
    a = ap.parse_args()
    print(json.dumps(main(a.dat.resolve(), a.instalado.resolve()), indent=1))
