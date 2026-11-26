#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""leer_avin.py - lector minimo de AVF_INFO/AVIN0001.INP (Sony A6000, fw 3.21).

Sin dependencias (solo stdlib). No fia la estructura: ancla en los nombres
ASCII que haya en el fichero y ensena, para cada uno, los campos del registro
deducido. Ver reports/film-pb-1-sub-avin-20261127.md.

Uso:
    python3 leer_avin.py AVIN0001.INP
    python3 leer_avin.py AVIN0001.INP --raw MAH04198      # volcado hex del registro
    python3 leer_avin.py AVIN0001.INP --header 0x100 --rec 0x80   # forzar rejilla

Estado de cada offset (V = verificado en libmpr.so, D = deducido):
    +0x00  char[0x12]  cDirPath            V  (0x1DE066, 0x1DE4CE: 18 B)
    +0x12  char[0x0E]  cFileName           V  (0x1DE080, 0x1DE4E8: 14 B)
    +0x20  u32         nFileSize           V  (0x1DE09C)
    +0x28  u32         nWidth              V  (0x1DE0B6)
    +0x2C  u32         nHeight             V  (0x1DE0D0)
    +0x30  u32         nDuration (ms)      V  (0x1DE0E4)
    +0x38  u32         emVideoCodec        V  (0x1DE104)
    +0x34  u32         nDuration90kHz      D  (2.o candidato de duracion)
    +0x24  u8          bValid              D
    tamano de registro 0x80 = 128          D  (.data 0x9D1280 del descriptor)
Lo 'V' es la estructura que consume el volcado [Avi][Mon]; que el fichero
use exactamente la misma es NO_VERIFICADO (no hay tarjeta).
"""
import argparse
import re
import struct
import sys

# --- estructura deducida del registro por clip (base = inicio del registro) ---
REC = [
    # nombre, offset, tipo
    ("cDirPath", 0x00, "char[18]"),
    ("cFileName", 0x12, "char[14]"),
    ("nFileSize", 0x20, "u32"),
    ("bValid?", 0x24, "u8"),
    ("nWidth", 0x28, "u32"),
    ("nHeight", 0x2C, "u32"),
    ("nDuration_ms", 0x30, "u32"),
    ("nDuration90kHz?", 0x34, "u32"),
    ("emVideoCodec", 0x38, "u32"),
]
NAME_OFF = 0x12          # offset del nombre dentro del registro
NAME_LEN = 0x0E          # capacidad maxima del nombre (13 utiles + NUL)
REC_SIZE = 0x80          # 128 B: valor 0x80 del descriptor .data 0x9D1280
NAME_RE = re.compile(rb"[A-Z0-9]{4}[0-9]{4}\.[A-Z0-9]{3}")
# file-ID de 16 B del descriptor .data 0x9D1298 (bytes tal cual, y su inverso)
GUID_LE = bytes.fromhex("ff067581fa7be290452784b05e6110ad")
GUID_BE = bytes.fromhex("817506ff90e27bfab0842745ad10615e")


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0] if o + 4 <= len(b) else None


def s(b, o, n):
    raw = b[o:o + n]
    return raw.split(b"\0")[0].decode("latin1", "replace")


def fmt_dur(ms, unit):
    if not ms or ms == 0xFFFFFFFF:
        return "----"
    sec = ms / float(unit)
    if sec > 86400:            # no es una duracion: filtro de ruido
        return "%d (?)" % ms
    return "%.3fs" % sec


def scan_names(data):
    """Devuelve [(offset_del_nombre, nombre)] de todos los nombres tipo Sony."""
    out, pos = [], 0
    while True:
        m = NAME_RE.search(data, pos)
        if not m:
            return out
        out.append((m.start(), m.group().decode("latin1")))
        pos = m.end()


def dump_rec(data, base, n=REC_SIZE):
    blk = data[base:base + n]
    out = []
    for i in range(0, len(blk), 16):
        ch = blk[i:i + 16]
        hexa = " ".join("%02x" % c for c in ch).ljust(47)
        txt = "".join(chr(c) if 32 <= c < 127 else "." for c in ch)
        out.append("    %04x  %s |%s|" % (i, hexa, txt))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Lector de AVF_INFO/AVIN0001.INP")
    ap.add_argument("fichero")
    ap.add_argument("--header", default=None,
                    help="tamano de cabecera en hex si se conoce (p.ej. 0x100)")
    ap.add_argument("--rec", default=None, help="tamano de registro (p.ej. 0x80)")
    ap.add_argument("--raw", default=None, metavar="NOMBRE",
                    help="volcar en hex el registro de ese nombre")
    a = ap.parse_args()

    data = open(a.fichero, "rb").read()
    print("fichero : %s" % a.fichero)
    print("tamano  : %d B (0x%X)" % (len(data), len(data)))
    print("")

    hits = []
    for tag, pat in (("LE", GUID_LE), ("BE", GUID_BE), ("LE[4:]", GUID_LE[4:])):
        i = data.find(pat)
        if i >= 0:
            hits.append("%s@0x%X" % (tag, i))
    print("file-ID del descriptor (16 B): %s" %
          (", ".join(hits) if hits else "NO encontrado"))
    print("")

    names = scan_names(data)
    if not names:
        print("no hay nombres tipo Sony en el fichero: nada que listar")
        return 1

    print("registros de clip (base = nombre - 0x%02X):" % NAME_OFF)
    hdr = ("  #  base    nombre         nFileSize   WxH         "
           "dur_ms          dur_90kHz       bValid?")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for i, (off, nm) in enumerate(names):
        base = off - NAME_OFF
        if base < 0:
            continue
        b = data[base:base + REC_SIZE]
        size = u32(b, 0x20)
        w, h = u32(b, 0x28), u32(b, 0x2C)
        dms, d90 = u32(b, 0x30), u32(b, 0x34)
        val = b[0x24] if len(b) > 0x24 else 0xFF
        print("%3d  %06X  %-14s %-11s %-11s %-15s %-15s 0x%02X" % (
            i, base, nm,
            size if size not in (None, 0xFFFFFFFF) else "----",
            "%dx%d" % (w, h) if w not in (None, 0xFFFFFFFF) else "----",
            "%d=%s" % (dms, fmt_dur(dms, 1000.0)) if dms is not None else "----",
            "%d=%s" % (d90, fmt_dur(d90, 90000.0)) if d90 is not None else "----",
            val))
        if a.header is not None:
            hsz = int(a.header, 16)
            k = (off - hsz - NAME_OFF) // REC_SIZE
            print("       rejilla: cabecera 0x%X + registro %d * 0x%X = 0x%X" % (
                hsz, k, REC_SIZE, hsz + k * REC_SIZE))
    print("")

    # tabla de offsets utiles del primer registro, para leer a mano
    print("campos del registro (base = offset del nombre - 0x%02X):" % NAME_OFF)
    for nm, o, t in REC:
        print("  +0x%02X  %-7s %s" % (o, t, nm))
    print("")

    if a.raw:
        want = a.raw.upper()
        for off, nm in names:
            if nm.upper().startswith(want[:12]):
                base = off - NAME_OFF
                print("volcado de %s (base 0x%X):" % (nm, base))
                print(dump_rec(data, base))
                break
        else:
            print("no encontrado: %s" % a.raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
