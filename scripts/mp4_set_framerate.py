#!/usr/bin/env python3
"""Reescribe la cadencia declarada de un MP4 de Sony sin tocar sus cajas propietarias.

Cambia `mdhd.timescale` y `mdhd.duration` de la pista de vídeo (timescale = delta
de muestra x fps pedidos) y deja intactas las cajas `uuid`, `MSNV`, `PROF`, `USMT`
y `MTDT` que el lector de la cámara verifica antes de reproducir. El fichero de
salida tiene el mismo tamaño: solo se reescriben valores de 32 bits in situ.

Sirve para probar si la guarda de contenido acepta un clip de otra cadencia
(ver reports/film-pb-1-causa-sistema-tv-20261127.md).

Uso:
    mp4_set_framerate.py ENTRADA SALIDA --fps 25
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

CONTENEDORES = {b"moov", b"trak", b"mdia", b"minf", b"stbl", b"edts"}


def cajas(datos: bytes, ini: int, fin: int):
    """Recorre las cajas de [ini, fin): (tipo, inicio_cuerpo, fin)."""
    pos = ini
    while pos + 8 <= fin:
        tam, tipo = struct.unpack_from(">I4s", datos, pos)
        cabecera = 8
        if tam == 1:
            tam = struct.unpack_from(">Q", datos, pos + 8)[0]
            cabecera = 16
        elif tam == 0:
            tam = fin - pos
        if tam < cabecera or pos + tam > fin:
            return
        yield tipo, pos + cabecera, pos + tam
        pos += tam


def buscar(datos: bytes, ini: int, fin: int, ruta: list[bytes]):
    """Cajas que casan con la ruta de tipos: (inicio_cuerpo, fin)."""
    for tipo, cuerpo, fin_caja in cajas(datos, ini, fin):
        if tipo != ruta[0]:
            continue
        if len(ruta) == 1:
            yield cuerpo, fin_caja
        elif tipo in CONTENEDORES:
            yield from buscar(datos, cuerpo, fin_caja, ruta[1:])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--fps", type=float, required=True, help="cadencia a declarar, p. ej. 25")
    args = ap.parse_args()

    original = Path(args.entrada).read_bytes()
    datos = bytearray(original)
    moov = next(buscar(datos, 0, len(datos), [b"moov"]), None)
    if moov is None:
        print("error: no hay caja moov", file=sys.stderr)
        return 2
    moov_cuerpo, moov_fin = moov

    cambios = 0
    for trak_cuerpo, trak_fin in buscar(datos, moov_cuerpo, moov_fin, [b"trak"]):
        hdlr = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"hdlr"]), None)
        if hdlr is None or datos[hdlr[0] + 8 : hdlr[0] + 12] != b"vide":
            continue
        mdhd = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"mdhd"]), None)
        stts = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"minf", b"stbl", b"stts"]), None)
        if mdhd is None or stts is None:
            continue
        cuerpo, _ = mdhd
        if struct.unpack_from(">I", datos, stts[0] + 4)[0] == 0:
            continue
        delta = struct.unpack_from(">I", datos, stts[0] + 12)[0]  # primer delta de muestra
        if delta == 0:
            continue
        version = datos[cuerpo]
        off_ts = cuerpo + (4 + 16 if version == 1 else 4 + 8)
        ts_viejo = struct.unpack_from(">I", datos, off_ts)[0]
        dur_vieja = struct.unpack_from(">I" if version == 0 else ">Q", datos, off_ts + 4)[0]
        ts_nuevo = round(delta * args.fps)
        if not 0 < ts_nuevo <= 0xFFFFFFFF:
            print(f"error: timescale fuera de rango ({ts_nuevo})", file=sys.stderr)
            return 2
        struct.pack_into(">I", datos, off_ts, ts_nuevo)
        # los deltas de stts no cambian: duration sigue siendo la misma suma de unidades
        print(f"vídeo: timescale {ts_viejo} -> {ts_nuevo} (delta {delta}, {args.fps:g} fps); duration {dur_vieja} queda igual y el clip dura {dur_vieja / ts_nuevo:.3f} s")
        cambios += 1

    if cambios == 0:
        print("error: no se reescribió ninguna pista de vídeo", file=sys.stderr)
        return 2
    if len(datos) != len(original):
        print("error: el tamaño cambió", file=sys.stderr)
        return 2
    Path(args.salida).write_bytes(bytes(datos))
    print(f"escrito {args.salida} ({len(datos)} B, mismas cajas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
