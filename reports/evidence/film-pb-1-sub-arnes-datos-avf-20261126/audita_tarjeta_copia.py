#!/usr/bin/env python3
"""COPIA de scripts/filmpb1_audita_tarjeta.py con UN cambio (sorted con key, 3 lineas)

FILM-PB-1: audita una copia de la tarjeta de la A6000 y dictamina si el índice AV miente.

Uso:
    filmpb1_audita_tarjeta.py <raiz_del_volumen> [--json]

`<raiz_del_volumen>` es la carpeta donde se copió el contenido de la tarjeta
(debe contener `AVF_INFO/` y `MP_ROOT/` o `PRIVATE/`).

Comprueba, para cada clip del índice `AVF_INFO/AVIN0001.INP`:
  * que el fichero exista en la ruta que dice el índice,
  * que el tamaño coincida con `nFileSize`,
  * que la duración del índice (`nDuration`, ms) coincida con la del `mvhd` del MP4.

La rejilla del registro (0x80 B) está verificada en
`reports/film-pb-1-sub-avin-20261127.md`: +0x00 cDirPath[0x12], +0x12 cFileName[0x0E],
+0x20 nFileSize, +0x24 bValid, +0x28 nWidth, +0x2C nHeight, +0x30 nDuration(ms).
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

REG = 0x80
NOMBRE = re.compile(rb"[A-Z0-9]{4}[0-9]{4}\.(?:MP4|M4V|MTS|M2TS)")
TOLERANCIA_MS = 100


def duracion_mvhd(datos: bytes) -> float | None:
    """Duración en segundos del primer `mvhd` del fichero (0 si es v1 o no está)."""
    i = 0
    while True:
        j = datos.find(b"mvhd", i)
        if j < 0:
            return None
        cuerpo = j + 4
        if cuerpo + 20 > len(datos):
            return None
        version = datos[cuerpo]
        if version == 0:
            timescale, dur = struct.unpack(">II", datos[cuerpo + 12:cuerpo + 20])
        elif version == 1:
            timescale = struct.unpack(">I", datos[cuerpo + 20:cuerpo + 24])[0]
            dur = struct.unpack(">Q", datos[cuerpo + 24:cuerpo + 32])[0]
        else:
            i = j + 4
            continue
        return dur / timescale if timescale else None


def registros(datos: bytes) -> list[dict]:
    salida = []
    for m in NOMBRE.finditer(datos):
        base = m.start() - 0x12
        if base < 0 or base + REG > len(datos):
            continue
        reg = datos[base:base + REG]
        salida.append({
            "base_hex": f"0x{base:06x}",
            "dir": reg[0x00:0x12].split(b"\0")[0].decode("latin1"),
            "fichero": reg[0x12:0x20].split(b"\0")[0].decode("latin1"),
            "tamano": struct.unpack("<I", reg[0x20:0x24])[0],
            "valido": reg[0x24],
            "ancho": struct.unpack("<I", reg[0x28:0x2C])[0],
            "alto": struct.unpack("<I", reg[0x2C:0x30])[0],
            "duracion_ms": struct.unpack("<I", reg[0x30:0x34])[0],
        })
    return salida


def audita(raiz: Path) -> dict:
    inp = raiz / "AVF_INFO" / "AVIN0001.INP"
    informe: dict = {"raiz": str(raiz), "avf_info": [], "clips": [], "avisos": []}
    if not inp.is_file():
        informe["avisos"].append("falta AVF_INFO/AVIN0001.INP")
        return informe
    avf = raiz / "AVF_INFO"
    informe["avf_info"] = sorted(
        ({"fichero": p.name, "bytes": p.stat().st_size} for p in avf.iterdir() if p.is_file()),
        key=lambda d: d["fichero"],
    )
    for reg in registros(inp.read_bytes()):
        item = dict(reg)
        ruta = None
        for prefijo in (raiz / reg["dir"], raiz / reg["dir"].replace("\\", "/"), raiz):
            cand = prefijo / reg["fichero"]
            if cand.is_file():
                ruta = cand
                break
        item["encontrado"] = ruta is not None
        if ruta is None:
            informe["avisos"].append(f"{reg['fichero']}: el índice lo lista y no está en disco")
        else:
            item["tamano_disco"] = ruta.stat().st_size
            if item["tamano"] and item["tamano"] != item["tamano_disco"]:
                informe["avisos"].append(
                    f"{reg['fichero']}: índice {item['tamano']} B / disco {item['tamano_disco']} B"
                )
            dur = None
            with ruta.open("rb") as fh:      # el `moov` puede estar al principio o al final
                for donde in (0, None):
                    if donde is None:
                        tam = ruta.stat().st_size
                        fh.seek(max(0, tam - 8_000_000))
                    dur = duracion_mvhd(fh.read(8_000_000))
                    if dur is not None:
                        break
            item["duracion_mvhd_s"] = None if dur is None else round(dur, 4)
            if dur is not None and reg["duracion_ms"]:
                delta = abs(reg["duracion_ms"] - dur * 1000)
                item["delta_ms"] = round(delta, 1)
                if delta > TOLERANCIA_MS:
                    informe["avisos"].append(
                        f"{reg['fichero']}: índice {reg['duracion_ms']} ms / mvhd {dur * 1000:.0f} ms"
                    )
        if not reg["valido"]:
            informe["avisos"].append(f"{reg['fichero']}: bValid=0 en el índice")
        informe["clips"].append(item)
    return informe


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    r = audita(Path(argv[1]))
    if "--json" in argv:
        print(json.dumps(r, indent=1, ensure_ascii=False))
    else:
        print(f"raíz: {r['raiz']}")
        print(f"AVF_INFO: {[x['fichero'] for x in r['avf_info']] or 'ausente'}")
        for c in r["clips"]:
            print(
                f"  {c['fichero']:14s} dir={c['dir']:16s} indice={c['duracion_ms']:7d} ms "
                f"mvhd={c.get('duracion_mvhd_s')} s tam={c['tamano']} disco={c.get('tamano_disco')} "
                f"bValid={c['valido']}"
            )
        print(f"avisos: {len(r['avisos'])}")
        for a in r["avisos"]:
            print("  -", a)
    return 0 if not r["avisos"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
