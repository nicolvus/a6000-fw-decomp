#!/usr/bin/env python3
"""S165 — utilidades comunes (sólo bytes, sin REA/Ghidra).

Base de la imagen: vaddr = 0x43541000 + file_offset (verificada en S70 y siguientes).
"""
import json
import struct

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
B = open(BIN, "rb").read()
N = len(B)
U16 = struct.Struct("<H").unpack_from
U32 = struct.Struct("<I").unpack_from

# mapa global de referencias PIC (regla estricta canónica, S106)
PIC = json.load(open("analysis/s106_imaging_cap/pic_refs_strict_global.json"))
PIC_INT = {int(k, 16): v for k, v in PIC.items()}

A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


def cstr(addr, blob=None):
    blob = B if blob is None else blob
    o = addr - BASE
    if o < 0 or o >= len(blob):
        return None
    e = blob.find(b"\x00", o)
    if e < 0:
        return None
    try:
        return blob[o:e].decode("utf-8")
    except UnicodeDecodeError:
        return None


def pic_ldr_sites(lo, hi):
    """[(addr, reg, valor_literal, dir_literal)] de `ldr rX,[pc,#imm]`."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = U16(B, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= N - 4:
            out.append((a, reg, U32(B, lit - BASE)[0], lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
    """[(addr, reg)] de los `add rX, pc` de 16 bits."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 4:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def func_starts(lo, hi):
    """Candidatos a inicio de función: prólogos Thumb `push {...,lr}` / `stmdb sp!,{...,lr}`.

    Devuelve [(addr, tipo)] ordenado. Heurística (la misma que usa S156): no es un
    mapa de funciones autoritativo, se valida a mano en los casos decisivos.
    """
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > N - 8:
            a += 2
            continue
        h = U16(B, o)[0]
        if (h & 0xFE00) == 0xB400 and (h & 0x00FF) != 0 and (h & 0x0100):
            # push {rlist} con lr -> B4xx where bit8 (lr) == 1
            out.append((a, "push"))
        elif h == 0xE92D:
            h2 = U16(B, o + 2)[0]
            if h2 & 0x4000:   # PUSH.W con lr
                out.append((a, "stmdb"))
        a += 2
    return out


def func_start(addr, back=0x4000):
    """Prólogo Thumb más cercano hacia atrás (heurística S156)."""
    o = addr - BASE
    a = o - (o % 2)
    while a >= max(0, o - back):
        h1 = U16(B, a)[0]
        if (h1 & 0xFE00) == 0xB400 and (h1 & 0x0100):
            return BASE + a
        if h1 == 0xE92D:
            h2 = U16(B, o + 2)[0] if False else U16(B, a + 2)[0]
            if h2 & 0x4000:
                return BASE + a
        a -= 2
    return None
