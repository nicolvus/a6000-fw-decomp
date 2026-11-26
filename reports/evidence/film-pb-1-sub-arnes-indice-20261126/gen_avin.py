#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_avin.py - escribe un AVF_INFO/AVIN0001.INP SINTETICO con UN registro valido
para un clip de MP_ROOT, con la rejilla verificada de libmpr (fw 3.21).

La rejilla (V = verificado en libmpr.so, ver reports/film-pb-1-sub-avin-20261127.md):
    +0x00  char[0x12]  cDirPath          (0x1DE066/0x1DE4CE)
    +0x12  char[0x0E]  cFileName         (0x1DE080/0x1DE4E8)
    +0x20  u32         nFileSize         (0x1DE09C)
    +0x24  u8          bValid            (D)
    +0x28  u32         nWidth            (0x1DE0B6)
    +0x2C  u32         nHeight           (0x1DE0D0)
    +0x30  u32         nDuration (ms)    (0x1DE0E4)
    +0x34  u32         nDuration90kHz    (D)
    +0x38  u32         emVideoCodec      (0x1DE104, 4 = AVC)
    +0x3C  u32         emProfileIndication
Registro 0x80 B (descriptor .data 0x9D1270), cabecera 0x100 B (NO_VERIFICADO).

NO_VERIFICADO (lo que este fichero NO demuestra):
  * tamano y semantica de la cabecera (aqui 0x100 B: file-ID de 16 B del descriptor
    .data 0x9D1298 + version/recSize/max/count, valores NO leidos de un .INP real),
  * separador de cDirPath ('/' por la plantilla propia del binario
    0x7ACAEC "/MP_ROOT/100ANV01/MAH%05ld.MP4"; el volcado de CS_AviAcsr imprime
    "Prefix"/"Separator" (0x7A61xx), asi que la ruta puede ser relativa al prefijo),
  * que la camara acepte un indice escrito a mano (no hay .INP real en el repo).

Uso:
    python3 gen_avin.py SALIDA.INP [--dir /MP_ROOT/103ANV01] [--size N] [--shotgun]
    --shotgun  repite el registro cada 0x80 B desde 0x80 (cubre cabeceras que sean
               multiplo de 0x80 sin conocer cual es); solo para medir.
"""
import argparse
import struct

GUID = bytes.fromhex("ff067581fa7be290452784b05e6110ad")   # .data 0x9D1298 del descriptor
REC = 0x80
HEADER = 0x100


def registro(d, nombre, size, w, h, ms, codec, profile, valido):
    b = bytearray(REC)
    assert len(d) < 0x12 and len(nombre) < 0x0E, "no cabe en el registro"
    b[0x00:0x00 + len(d)] = d.encode()
    b[0x12:0x12 + len(nombre)] = nombre.encode()
    struct.pack_into("<I", b, 0x20, size)
    b[0x24] = valido
    struct.pack_into("<I", b, 0x28, w)
    struct.pack_into("<I", b, 0x2C, h)
    struct.pack_into("<I", b, 0x30, ms)              # ms
    struct.pack_into("<I", b, 0x34, ms * 90)          # 90 kHz (9510 ms -> 855900)
    struct.pack_into("<I", b, 0x38, codec)            # 4 = AVC
    struct.pack_into("<I", b, 0x3C, profile)          # 2 = MAIN (D)
    return bytes(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("--dir", default="/MP_ROOT/103ANV01")
    ap.add_argument("--nombre", default="MAH04198.MP4")
    ap.add_argument("--size", type=int, default=14545696)   # tamano real del MP4 del repo
    ap.add_argument("--w", type=int, default=1440)
    ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--ms", type=int, default=9510)          # 9,5095 s del mvhd
    ap.add_argument("--codec", type=int, default=4)          # AVC
    ap.add_argument("--profile", type=int, default=2)
    ap.add_argument("--valid", type=int, default=1)
    ap.add_argument("--header", type=lambda s: int(s, 0), default=HEADER)
    ap.add_argument("--shotgun", action="store_true")
    a = ap.parse_args()

    rec = registro(a.dir, a.nombre, a.size, a.w, a.h, a.ms, a.codec, a.profile, a.valid)
    hdr = bytearray(a.header)
    hdr[0:16] = GUID
    if a.header >= 0x20:
        struct.pack_into("<I", hdr, 0x10, 1)        # version
        struct.pack_into("<I", hdr, 0x14, REC)      # contentInfoSize
        struct.pack_into("<I", hdr, 0x18, 0x2710)   # max contenidos
        struct.pack_into("<I", hdr, 0x1C, 1)        # contentInfoCount = 1
    datos = bytearray(hdr)
    if a.shotgun:                                    # mismo registro en cada frontera de 0x80 desde 0x80
        while len(datos) < 0x800:
            datos += b"\0" * (REC - len(datos) % REC)
            datos += rec
    else:
        datos += rec
    with open(a.salida, "wb") as f:
        f.write(datos)
    print("escrito %s: %d B (cabecera 0x%X + registros de 0x80%s)" %
          (a.salida, len(datos), a.header, ", uno por frontera de 0x80" if a.shotgun else ""))


if __name__ == "__main__":
    main()
