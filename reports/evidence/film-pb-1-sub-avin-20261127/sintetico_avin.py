#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sintetico_avin.py - construye un AVIN0001.INP SINTETICO con la estructura
deducida (ver reports/film-pb-1-sub-avin-20261127.md) para probar leer_avin.py.

Nada de esto afirma que la camara escriba asi: sirve para fijar el formato que
el lector espera y poder contrastarlo con el fichero real cuando haya tarjeta.
"""
import struct
import sys

GUID = bytes.fromhex("ff067581fa7be290452784b05e6110ad")   # .data 0x9D1298
HEADER = 0x100        # DEDUCIDO: cabecera de 256 B antes del primer registro
REC = 0x80            # descriptor .data 0x9D1280

# (dir, nombre, tamano, ancho, alto, duracion_ms, codec, valido)
# duraciones reales de los 7 clips del 25-11 (informe de traspaso)
CLIPS = [
    ("MP_ROOT/100ANV01", "MAH04198.MP4", 24641536, 1440, 1080, 9510, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04200.MP4", 12984320, 1440, 1080, 5005, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04201.MP4", 63606784, 1440, 1080, 24525, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04202.MP4", 81805312, 1440, 1080, 31532, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04203.MP4", 89587712, 1440, 1080, 34535, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04204.MP4", 136306688, 1440, 1080, 52553, 4, 1),
    ("MP_ROOT/100ANV01", "MAH04205.MP4", 188227584, 1440, 1080, 72573, 4, 1),
    # caso de control: el clip con el punto de reanudacion a 2 s
    ("MP_ROOT/100ANV01", "MAH04199.MP4", 24641536, 1440, 1080, 2000, 4, 0),
]


def rec_bytes(c):
    d = bytearray(REC)
    d[0x00:0x00 + len(c[0])] = c[0].encode()
    d[0x12:0x12 + len(c[1])] = c[1].encode()
    struct.pack_into("<I", d, 0x20, c[2])       # nFileSize
    d[0x24] = c[7]                              # bValid? (deducido)
    struct.pack_into("<I", d, 0x28, c[3])       # nWidth
    struct.pack_into("<I", d, 0x2C, c[4])       # nHeight
    struct.pack_into("<I", d, 0x30, c[5])       # nDuration ms
    struct.pack_into("<I", d, 0x34, c[5] * 90)  # nDuration90kHz? = ms*90
    struct.pack_into("<I", d, 0x38, c[6])       # emVideoCodec=4 (AVC)
    struct.pack_into("<I", d, 0x3C, 2)          # emProfileIndication=MAIN
    return bytes(d)


def main(path):
    hdr = bytearray(HEADER)
    hdr[0:16] = GUID
    struct.pack_into("<I", hdr, 0x10, 0x00010001)   # version inventada
    struct.pack_into("<I", hdr, 0x14, len(CLIPS))   # contentInfoCount
    struct.pack_into("<I", hdr, 0x18, REC)          # contentInfoSize
    struct.pack_into("<I", hdr, 0x1C, 0x2710)       # max contenido
    with open(path, "wb") as f:
        f.write(hdr)
        for c in CLIPS:
            f.write(rec_bytes(c))
        f.write(b"\xff" * REC)                      # registro libre centinela
    print("escrito %s: %d B (cabecera 0x%X + %d registros de 0x%X)" % (
        path, HEADER + REC * (len(CLIPS) + 1), HEADER, len(CLIPS) + 1, REC))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "AVIN0001_sintetico.INP")
