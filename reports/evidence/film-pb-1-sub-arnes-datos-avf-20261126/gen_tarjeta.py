#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_tarjeta.py — árbol de tarjeta mínimo con el clip MAH04198.MP4 y su índice
`AVF_INFO/AVIN0001.INP` con la rejilla VERIFICADA de `libmpr.so` (fw 3.21).

Rejilla del registro (0x80 B), verificada en `reports/film-pb-1-sub-avin-20261127.md` §3:
    +0x00 char[0x12] cDirPath      (0x1DE066/0x1DE4CE)   ← relativa al prefijo del volumen
    +0x12 char[0x0E] cFileName     (0x1DE080/0x1DE4E8)
    +0x20 u32        nFileSize     (0x1DE09C)
    +0x24 u8         bValid
    +0x28 u32        nWidth        (0x1DE0B6)
    +0x2C u32        nHeight       (0x1DE0D0)
    +0x30 u32        nDuration ms  (0x1DE0E4)
    +0x34 u32        nDuration90kHz
    +0x38 u32        emVideoCodec  (4 = AVC)
    +0x3C u32        emProfileIndication

Cabecera: **NO VERIFICADA** (0x100 B: file-ID de 16 B del descriptor `.data` 0x9D1270,
versión, tamaño de registro, máximo y número de contenidos). Es la única pieza del
fichero que no sale de bytes del binario; el lector del repo (`filmpb1_audita_tarjeta.py`)
no la necesita porque ancla en el nombre ASCII.

Clip: MP4 sintético mínimo pero bien formado (`ftyp`/`mdat`/`moov` con `mvhd` y un
`trak` de vídeo `avc1` 1440×1080). Existe porque en el repo no hay ningún `.mp4` real.

Uso:
    python3 gen_tarjeta.py SALIDA_DIR [--dir MP_ROOT/100ANV01] [--ms 9510] [--bnp]

SALIDA_DIR queda con:
    AVF_INFO/AVIN0001.INP      (y .BNP con --bnp)
    MP_ROOT/<NNN>ANV01/MAH04198.MP4
    DCIM/100MSDCF/  PRIVATE/M4ROOT/{CLIP,SUB,THMBNL,GENERAL}   (estructura base)
"""
from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

GUID = bytes.fromhex("ff067581fa7be290452784b05e6110ad")  # file-ID de 16 B, .data 0x9D1270
REC = 0x80
CABECERA = 0x100


def caja(tipo: bytes, carga: bytes = b"") -> bytes:
    return struct.pack(">I", 8 + len(carga)) + tipo + carga


def mp4(ms: int, w: int, h: int, mdat: int) -> bytes:
    """MP4 mínimo: ftyp + mdat (ceros) + moov(mvhd, trak vídeo avc1). mvhd a 90 kHz."""
    ts = 90_000
    dur = round(ms * ts / 1000)  # 9510 ms -> 855900
    ftyp = caja(b"ftyp", b"MSNV" + struct.pack(">I", 0x015A0070) + b"MSNVmp42isom")
    mvhd = caja(b"mvhd", struct.pack(">IIIII", 0, 0, 0, ts, dur) + struct.pack(">I", 0x00010000)
                + struct.pack(">HH", 0x0100, 0) + b"\0" * 8
                + struct.pack(">9i", 0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000)
                + b"\0" * 24 + struct.pack(">I", 3))
    tkhd = caja(b"tkhd", struct.pack(">IIIII", 0x0000000F, 0, 0, 1, 0) + struct.pack(">I", dur)
                + b"\0" * 8 + struct.pack(">hhhh", 0, 0, 0x0100, 0)
                + struct.pack(">9i", 0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000)
                + struct.pack(">II", w << 16, h << 16))
    mdhd = caja(b"mdhd", struct.pack(">IIIII", 0, 0, 0, ts, dur) + struct.pack(">HH", 0x55C4, 0))
    hdlr = caja(b"hdlr", struct.pack(">II", 0, 0) + b"vide" + b"\0" * 12 + b"VideoHandler\0")
    vmhd = caja(b"vmhd", struct.pack(">IHHH", 0x00000001, 0, 0, 0))
    url_ = caja(b"url ", struct.pack(">I", 1))
    dref = caja(b"dref", struct.pack(">I", 0) + struct.pack(">I", 1) + url_)
    dinf = caja(b"dinf", dref)
    avc1 = caja(b"avc1", b"\0" * 6 + struct.pack(">H", 1) + b"\0" * 16
                + struct.pack(">HH", w, h) + struct.pack(">II", 0x00480000, 0x00480000)
                + struct.pack(">I", 0) + struct.pack(">H", 1) + b"\0" * 32
                + struct.pack(">HH", 0x0018, 0xFFFF)
                + caja(b"avcC", bytes([1, 0x64, 0, 0x1F, 0xFF, 0xE1, 0, 0, 0])))
    stsd = caja(b"stsd", struct.pack(">I", 0) + struct.pack(">I", 1) + avc1)
    stbl = caja(b"stbl", stsd
                + caja(b"stts", struct.pack(">II", 0, 0))
                + caja(b"stsc", struct.pack(">II", 0, 0))
                + caja(b"stsz", struct.pack(">II", 0, 0))
                + caja(b"stco", struct.pack(">II", 0, 0)))
    minf = caja(b"minf", vmhd + dinf + stbl)
    mdia = caja(b"mdia", mdhd + hdlr + minf)
    trak = caja(b"trak", tkhd + mdia)
    moov = caja(b"moov", mvhd + trak)
    return ftyp + caja(b"mdat", b"\0" * mdat) + moov


def mp4_info(f: Path) -> tuple[int, int, int]:
    """(ms, ancho, alto) leídos del propio fichero: `mvhd` y `tkhd` del primer `trak` de vídeo."""
    d = f.read_bytes()
    ms = w = h = 0
    j = d.find(b"mvhd")
    if j >= 0:
        c = j + 4
        if d[c] == 0:
            ts, dur = struct.unpack_from(">II", d, c + 12)
        else:
            ts = struct.unpack_from(">I", d, c + 20)[0]
            dur = struct.unpack_from(">Q", d, c + 24)[0]
        ms = round(dur * 1000 / ts) if ts else 0
    j = d.find(b"tkhd")
    if j >= 0:
        c = j + 4
        off = c + (76 if d[c] == 0 else 88)          # ancho/alto van al final de la caja, igual en v0 y v1
        w = struct.unpack_from(">I", d, off)[0] >> 16
        h = struct.unpack_from(">I", d, off + 4)[0] >> 16
    return ms, w, h


def registro(d: str, nombre: str, tam: int, w: int, h: int, ms: int, codec: int, perfil: int) -> bytes:
    b = bytearray(REC)
    assert len(d) < 0x12 and len(nombre) < 0x0E, "no cabe en el registro"
    b[0x00:len(d)] = d.encode("ascii")
    b[0x12:0x12 + len(nombre)] = nombre.encode("ascii")
    struct.pack_into("<I", b, 0x20, tam)
    b[0x24] = 1                                     # bValid
    struct.pack_into("<I", b, 0x28, w)
    struct.pack_into("<I", b, 0x2C, h)
    struct.pack_into("<I", b, 0x30, ms)
    struct.pack_into("<I", b, 0x34, round(ms * 90))  # 90 kHz
    struct.pack_into("<I", b, 0x38, codec)          # 4 = AVC
    struct.pack_into("<I", b, 0x3C, perfil)         # 2 = MAIN
    return bytes(b)


def indice(*regs: bytes) -> bytes:
    h = bytearray(CABECERA)
    h[0:16] = GUID
    struct.pack_into("<I", h, 0x10, 1)        # versión (NV)
    struct.pack_into("<I", h, 0x14, REC)      # contentInfoSize (D: descriptor 0x80)
    struct.pack_into("<I", h, 0x18, 0x2710)   # máximo de contenidos (D: descriptor)
    struct.pack_into("<I", h, 0x1C, len(regs))  # contentInfoCount
    return bytes(h) + b"".join(regs)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz")
    ap.add_argument("--dir", default="MP_ROOT/100ANV01", help="cDirPath tal cual va en el registro (sin barra inicial)")
    ap.add_argument("--nombre", default="MAH04198.MP4")
    ap.add_argument("--ms", type=int, default=9510)
    ap.add_argument("--w", type=int, default=1440)
    ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--extra-dir", action="append", default=[], metavar="DIR",
                    help="si ya existe <DIR>/<nombre>, añade otro registro con SU tamaño (para índices que cubren varias carpetas)")
    ap.add_argument("--mdat", type=int, default=14_540_000, help="bytes de mdat (el tamaño del clip sale de aquí)")
    ap.add_argument("--bnp", action=argparse.BooleanOptionalAction, default=True,
                    help="escribir AVIN0001.BNP (copia del .INP); --no-bnp lo omite")
    ap.add_argument("--extras", action=argparse.BooleanOptionalAction, default=True,
                    help="escribir AVIN0001.INT y PRV00001.BIN (file-ID + ceros): el invitado los sondea por nombre")
    a = ap.parse_args()

    raiz = Path(a.raiz).expanduser()
    for d in ("DCIM/100MSDCF", "PRIVATE/M4ROOT/CLIP", "PRIVATE/M4ROOT/SUB", "PRIVATE/M4ROOT/THMBNL",
              "PRIVATE/M4ROOT/GENERAL", "PRIVATE/AVCHD", "AVF_INFO", a.dir):
        (raiz / d).mkdir(parents=True, exist_ok=True)

    clip = raiz / a.dir / a.nombre
    clip.write_bytes(mp4(a.ms, a.w, a.h, a.mdat))
    recs = [registro(a.dir, a.nombre, clip.stat().st_size, a.w, a.h, a.ms, 4, 2)]
    for d in a.extra_dir:                      # copias que ya estén en la tarjeta: el índice las cubre con su tamaño real
        f = raiz / d / a.nombre
        if f.is_file():
            ms_f, w_f, h_f = mp4_info(f)            # la verdad del fichero, no la del patrón
            recs.append(registro(d, a.nombre, f.stat().st_size, w_f or a.w, h_f or a.h, ms_f or a.ms, 4, 2))
            print(f"  + registro extra: {d}/{a.nombre} ({f.stat().st_size} B, {w_f}x{h_f}, {ms_f} ms)")
    datos = indice(*recs) if len(recs) > 1 else indice(recs[0])
    inp = raiz / "AVF_INFO/AVIN0001.INP"
    inp.write_bytes(datos)
    if a.bnp:
        (raiz / "AVF_INFO/AVIN0001.BNP").write_bytes(datos)
    if a.extras:  # ficheros que el invitado nombra en el sondeo del directorio (medido: 06-corrida1-montaje-y-avf.txt)
        for n in ("AVIN0001.INT", "PRV00001.BIN"):
            (raiz / "AVF_INFO" / n).write_bytes(GUID + b"\0" * (CABECERA - 16))

    for f in sorted((raiz / "AVF_INFO").iterdir()) + [clip]:
        print(f"{f.stat().st_size:9d}  {hashlib.sha256(f.read_bytes()).hexdigest()[:16]}  {f}")
    print(f"registro: cDirPath={a.dir!r} cFileName={a.nombre!r} nFileSize={clip.stat().st_size} "
          f"nDuration={a.ms} ms Duration90kHz={round(a.ms * 90)} {a.w}x{a.h} codec=4(AVC) perfil=2(MAIN)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
