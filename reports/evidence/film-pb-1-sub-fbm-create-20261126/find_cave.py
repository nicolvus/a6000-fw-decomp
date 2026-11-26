#!/usr/bin/env python3
"""Busca un hueco ejecutable NO referenciado en libmpr.so 3.21 para la cueva del parche FBM.

Un candidato de N bytes a partir de `s` es válido si:
 1. cae en el PT_LOAD R+X (VA == offset de fichero; R+X hasta 0x9BB1C8) y dentro de .text o .rodata;
 2. sus N bytes son todos 0x00 (o todos 0xFF);
 3. ninguna entrada de .rel.dyn/.rel.plt tiene r_offset dentro;
 4. ningún `ldr rX,[pc,#imm]`, `ldr.w` ni `adr`/`adr.w` pc-relativo del binario apunta dentro
    (buscado por PATRÓN en todas las posiciones pares: el barrido lineal se desincroniza en las
    islas de literales de .text);
 5. ningún u32 del fichero vale una dirección de dentro (nadie guarda su puntero). Como el hueco
    es todo ceros, el patrón de cualquier dirección de dentro es no nulo: no puede estar dentro.
uso: find_cave.py BYTES
"""
import struct
import sys

import numpy as np

sys.path.insert(0, "reports/evidence/film-pb-1-sub-fbm-create-20261126")
from elfh import Elf  # noqa: E402

LIB = "analysis/camera-extract/usr/lib/libmpr.so"
RX_END = 0x9BB1C8  # PT_LOAD 1: off=0 vaddr=0 filesz=memsz=0x9BB1C8 flags=5 (R+X)

e = Elf(LIB)
d = e.d
want = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0x18

hw = np.frombuffer(d[:RX_END], dtype="<u2")           # medias palabras
w = np.frombuffer(d[:RX_END & ~3], dtype="<u4")            # palabras
addr = np.arange(len(hw), dtype=np.uint64) * 2
base = (addr + 4) & ~np.uint64(3)

tgt = []
m = (hw & 0xF800) == 0x4800                            # LDR Rt,[pc,#imm8*4]
tgt.append(base[m] + (hw[m] & 0xFF).astype(np.uint64) * 4)
m = hw == 0xF8DF                                       # LDR.W Rt,[pc,#+imm12]
tgt.append(base[m] + (hw[np.minimum(np.nonzero(m)[0] + 1, len(hw) - 1)] & 0xFFF).astype(np.uint64))
m = (hw & 0xFF7F) == 0xF85F                            # LDR.W Rt,[pc,#-imm12]
tgt.append(base[m] - (hw[np.minimum(np.nonzero(m)[0] + 1, len(hw) - 1)] & 0xFFF).astype(np.uint64))
m = (hw & 0xF800) == 0xA000                            # ADR
tgt.append(base[m] + (hw[m] & 0xFF).astype(np.uint64) * 4)
LITS = np.unique(np.concatenate(tgt))

VALS = np.unique(w)                                     # todos los u32 presentes en el fichero

RELS = []
for sec in (".rel.dyn", ".rel.plt"):
    _, off, size = e.sec[sec]
    r = np.frombuffer(d[off:off + size], dtype="<u4")[0::2]
    RELS.append(r)
RELS = np.unique(np.concatenate(RELS))

zero = (w == 0) | (w == 0xFFFFFFFF)


def run_end(s):
    """longitud del tramo de palabras iguales que empieza en la palabra s (s múltiplo de 4)."""
    v = w[s // 4]
    k = s // 4
    while k < len(w) and w[k] == v:
        k += 1
    return k * 4


TEXT = (0x120228, 0x7A3E84)
RODATA = (0x7A3E90, 0x956750)


def donde(s, e2):
    return " .text" if TEXT[0] <= s and e2 <= TEXT[1] else (" .rodata" if RODATA[0] <= s and e2 <= RODATA[1] else None)


cands = []
for s in range(0, RX_END - want, 4):
    if donde(s, s + want) is None:
        continue
    if not zero[s // 4]:
        continue
    if run_end(s) < want:
        continue
    e2 = s + want
    if np.any((RELS >= s) & (RELS < e2)):
        continue
    if np.any((LITS >= s) & (LITS < e2)):
        continue
    if np.any((VALS >= s) & (VALS < e2)):
        continue
    cands.append(s)

cands.sort(key=lambda s: -run_end(s - (s % 4)))
print("huecos validos de %#x B en .text/.rodata: %d" % (want, len(cands)))
for s in cands[:30]:
    sec = next((n for n, (va, off, sz) in e.sec.items() if sz and va <= s < va + sz), "?")
    run = run_end(s - (s & 3))
    ini = s
    while ini > 0 and d[ini - 1] == d[s]:
        ini -= 1
    print("  %08x..%08x  relleno %02x  tramo %08x..%08x (%#x B)  seccion %s" % (
        s, s + want, d[s], ini, run if run > s else s + want, run - (s - ini), sec))
