#!/usr/bin/env python3
"""FILM-PB-1 (26-11) — qué miembros cambian entre el `firmware.tar` del paquete INSTALADO (3.93) y el del paquete limpio (3.94).

Compara cabecera y SHA-256 de cada miembro con `mmap` (los dos tars suman 424 MB). Uso: comparar_tars.py → JSON a stdout.
"""
import hashlib
import json
import mmap
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from e25_27 import tarball

INSTALADO = ROOT / "build/cfw_func393/pp/pkg-3.93/firmware.tar"
LIMPIO = ROOT / "build/cfw_avcam_limpio/pkg-3.94/firmware.tar"
CHUNK = 1 << 20


def miembros(ruta: Path):
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
            yield nombre, cab, tam, h.hexdigest()
            pos += 512 + ((tam + 511) // 512) * 512


def main() -> dict:
    a = list(miembros(INSTALADO))
    b = list(miembros(LIMPIO))
    na, nb = [x[0] for x in a], [x[0] for x in b]
    mismos_orden = na == nb
    cambios = []
    for x, y in zip(a, b):
        if x[1] != y[1] or x[3] != y[3]:
            cambios.append({"miembro": x[0], "bytes_antes": x[2], "bytes_despues": y[2],
                            "sha256_antes": x[3], "sha256_despues": y[3], "cabecera_distinta": x[1] != y[1]})
    return {"instalado": str(INSTALADO), "limpio": str(LIMPIO), "miembros": len(a),
            "mismo_numero": len(a) == len(b), "mismo_orden": mismos_orden,
            "quitados": sorted(set(na) - set(nb)), "anadidos": sorted(set(nb) - set(na)),
            "cambiados": cambios,
            "intactos": sorted(set(na) & set(nb) - {c["miembro"] for c in cambios})}


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
