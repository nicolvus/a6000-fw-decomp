#!/usr/bin/env python3
"""Busca en un ELF (biblioteca de la camara) las cadenas/cajas del parser MP4.

Uso: clip-scanlib.py <lib.so> [--all]
Salida: por cada aguja, offsets de fichero (y VA estimada via PT_LOAD) donde
aparece el patron literal, y contexto imprimible.
"""
import struct
import sys

AGUJAS = [
    b"ftyp", b"moov", b"mdat", b"moof", b"mvex", b"mvhd", b"trak", b"mdia",
    b"minf", b"stbl", b"stsd", b"stts", b"stsc", b"stsz", b"stco", b"stss",
    b"ctts", b"elst", b"edts", b"udta", b"uuid", b"avcC", b"hvcC", b"mvhd",
    b"MSNV", b"mp42", b"isom", b"XAVC", b"xavc", b"AVC ", b"avc1", b"mp4a",
    b"esds", b"dinf", b"dref", b"vmhd", b"smhd", b"hdlr", b"mdhd", b"tkhd",
    b"mfra", b"mfro", b"wide", b"free", b"skip", b"MSNV", b"Main", b"High",
    b"Baseline", b"PROF", b"USMT", b"MTDT", b"FPRF", b"APRF", b"VPRF",
    b"Detect UnSupported Content", b"UnSupported", b"not supported",
    b"Unsupported", b"movie", b"Movie",
]


def segs(d):
    e_phoff = struct.unpack_from("<I", d, 28)[0]
    e_phentsize = struct.unpack_from("<H", d, 42)[0]
    e_phnum = struct.unpack_from("<H", d, 44)[0]
    out = []
    for i in range(e_phnum):
        o = e_phoff + i * e_phentsize
        t, off, va, pa, fsz, msz, fl, al = struct.unpack_from("<8I", d, o)
        if t == 1:
            out.append((off, va, fsz))
    return out


def va_of(seg, off):
    for po, va, fsz in seg:
        if po <= off < po + fsz:
            return va + (off - po)
    return None


def ctx(d, off, n=48):
    a = max(0, off - n)
    b = min(len(d), off + n)
    return d[a:b]


def main():
    fn = sys.argv[1]
    d = open(fn, "rb").read()
    sg = segs(d)
    print("# %s size=%d" % (fn, len(d)))
    for ag in AGUJAS:
        pos = []
        i = d.find(ag)
        while i >= 0 and len(pos) < 8:
            pos.append(i)
            i = d.find(ag, i + 1)
        if not pos:
            continue
        tot = d.count(ag)
        print("== %r total=%d" % (ag, tot))
        for p in pos:
            v = va_of(sg, p)
            c = ctx(d, p)
            s = "".join(chr(x) if 32 <= x < 127 else "." for x in c)
            print("   off=%#x va=%s | %s" % (p, hex(v) if v else "-", s))


if __name__ == "__main__":
    main()
