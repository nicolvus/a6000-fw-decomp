#!/usr/bin/env python3
"""Reescribe la cadencia declarada de un MP4 de Sony sin tocar sus cajas propietarias.

Cambia la pista de vídeo para que declare otra cadencia y deja el resto de campos de
tiempo coherentes con ella:

- `mdia.mdhd`: `timescale` = delta de muestra x fps pedidos, `duration` intacta (la
  misma suma de unidades, que ahora son más lentas);
- `tkhd.duration` y `edts.elst.segment_duration` del vídeo: reescalados a la nueva
  duración real (si coincidían con la vieja, para no romper ficheros ya editados);
- `mvhd.duration`: la mayor de las pistas.

No toca el audio, ni `stts`, ni las cajas `uuid`, `MSNV`, `PROF`, `USMT` y `MTDT` que el
lector de la cámara verifica. El tamaño del fichero no cambia: solo valores de 32 bits.

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


def leer_mvhd(datos: bytes, cuerpo: int) -> tuple[int, int, int]:
    """(desplazamiento del timescale, desplazamiento de duration, timescale)."""
    version = datos[cuerpo]
    off_ts = cuerpo + (20 if version == 1 else 12)
    off_dur = off_ts + 4
    return off_ts, off_dur, struct.unpack_from(">I", datos, off_ts)[0]


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
    mvhd = next(buscar(datos, moov_cuerpo, moov_fin, [b"mvhd"]), None)
    if mvhd is None:
        print("error: no hay caja mvhd", file=sys.stderr)
        return 2
    _, off_mvhd_dur, mvhd_ts = leer_mvhd(datos, mvhd[0])

    cambios = []
    for trak_cuerpo, trak_fin in buscar(datos, moov_cuerpo, moov_fin, [b"trak"]):
        hdlr = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"hdlr"]), None)
        es_video = hdlr is not None and datos[hdlr[0] + 8 : hdlr[0] + 12] == b"vide"
        mdhd = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"mdhd"]), None)
        tkhd = next(buscar(datos, trak_cuerpo, trak_fin, [b"tkhd"]), None)
        elst = next(buscar(datos, trak_cuerpo, trak_fin, [b"edts", b"elst"]), None)
        if mdhd is None or tkhd is None:
            continue

        cuerpo = mdhd[0]
        version = datos[cuerpo]
        off_ts = cuerpo + (4 + 16 if version == 1 else 4 + 8)
        off_dur = off_ts + 4
        ts_viejo = struct.unpack_from(">I", datos, off_ts)[0]
        dur_vieja = struct.unpack_from(">I" if version == 0 else ">Q", datos, off_dur)[0]

        if es_video:
            stts = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"minf", b"stbl", b"stts"]), None)
            if stts is None or struct.unpack_from(">I", datos, stts[0] + 4)[0] == 0:
                print("error: pista de vídeo sin stts utilizable", file=sys.stderr)
                return 2
            delta = struct.unpack_from(">I", datos, stts[0] + 12)[0]
            if delta == 0:
                print("error: delta de muestra cero", file=sys.stderr)
                return 2
            ts_nuevo = round(delta * args.fps)
            if not 0 < ts_nuevo <= 0xFFFFFFFF:
                print(f"error: timescale fuera de rango ({ts_nuevo})", file=sys.stderr)
                return 2
            struct.pack_into(">I", datos, off_ts, ts_nuevo)
            dur_real_nueva = dur_vieja / ts_nuevo
            dur_real_vieja = dur_vieja / ts_viejo
            cambios.append(f"vídeo: timescale {ts_viejo} -> {ts_nuevo} (delta {delta}, {args.fps:g} fps), {dur_real_vieja:.3f} s -> {dur_real_nueva:.3f} s")

            for nombre, caja in (("tkhd", tkhd), ("elst", elst)):
                if caja is None:
                    continue
                c = caja[0]
                if nombre == "tkhd":
                    v = datos[c]
                    off = c + (28 if v == 1 else 20)
                    fmt, leido = (">Q" if v == 1 else ">I"), struct.unpack_from(">I" if v == 0 else ">Q", datos, off)[0]
                else:
                    v = datos[c]
                    if struct.unpack_from(">I", datos, c + 4)[0] != 1:
                        continue
                    off = c + 8
                    fmt, leido = ">I", struct.unpack_from(">I", datos, off)[0]
                esperado = round(dur_real_vieja * mvhd_ts)
                if abs(leido - esperado) > 1:
                    print(f"  aviso: {nombre} del vídeo no coincide con el mdhd ({leido} frente a {esperado}); no se toca")
                    continue
                struct.pack_into(fmt, datos, off, round(dur_real_nueva * mvhd_ts))
                cambios.append(f"  {nombre}.duration {leido} -> {round(dur_real_nueva * mvhd_ts)}")

    # mvhd.duration = mayor duración de las pistas, en la escala del mvhd
    total = 0
    for trak_cuerpo, trak_fin in buscar(datos, moov_cuerpo, moov_fin, [b"trak"]):
        mdhd = next(buscar(datos, trak_cuerpo, trak_fin, [b"mdia", b"mdhd"]), None)
        if mdhd is None:
            continue
        c = mdhd[0]
        v = datos[c]
        off_ts = c + (4 + 16 if v == 1 else 4 + 8)
        ts = struct.unpack_from(">I", datos, off_ts)[0]
        dur = struct.unpack_from(">I" if v == 0 else ">Q", datos, off_ts + 4)[0]
        total = max(total, round(dur / ts * mvhd_ts))
    viejo = struct.unpack_from(">I", datos, off_mvhd_dur)[0]
    struct.pack_into(">I", datos, off_mvhd_dur, total)
    cambios.append(f"mvhd.duration {viejo} -> {total} (escala {mvhd_ts})")

    if len(datos) != len(original):
        print("error: el tamaño cambió", file=sys.stderr)
        return 2
    Path(args.salida).write_bytes(bytes(datos))
    for linea in cambios:
        print(linea)
    print(f"escrito {args.salida} ({len(datos)} B, mismas cajas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
