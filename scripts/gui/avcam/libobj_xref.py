#!/usr/bin/env python3
"""Xrefs estáticas sobre `libObj.so` 3.21 (Capstone/NumPy, sin REA; E2E-3, g75 T71).

uso: libobj_xref.py str «texto»   → cadenas que lo contienen y las funciones (Thumb, `ldr+add pc`) que las usan
     libobj_xref.py call 0xADDR…  → llamadores `bl`/`b.w` Thumb de cada función
     libobj_xref.py dis  0xA 0xB  → desensamblado Thumb de [A, B)
NOTA: segmento RW con vaddr = offset + 0x8000 (tablas/GOT); el texto tiene vaddr = offset. Límite: no ve llamadas ARM ni indirectas (vtables).
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

import numpy as np
from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

LIB = Path(__file__).resolve().parents[3] / "analysis/camera-extract/usr/lib/libObj.so"
RAW = LIB.read_bytes()
TEXTO = RAW[:0xE1A000]
_W = np.frombuffer(TEXTO[: len(TEXTO) // 4 * 4], dtype="<u4").astype(np.int64)
_POS = np.arange(len(_W)) * 4


def inicio_cadena(o: int) -> int:
    while RAW[o - 1]:
        o -= 1
    return o


def xrefs_cadena(t: int) -> list[int]:
    """Direcciones del `add rX, pc` que apunta a la cadena `t` (la palabra literal es `t - (add+4)`)."""
    a = (t - _W - 4) & 0xFFFFFFFF
    ok = np.nonzero((a % 2 == 0) & (a < _POS) & (_POS - a < 1100))[0]
    return [int(a[i]) for i in ok if (struct.unpack_from("<H", TEXTO, int(a[i]))[0] & 0xFF78) == 0x4478]


def _sx(v: int, b: int) -> int:
    return v - (1 << b) if v & (1 << (b - 1)) else v


def llamadores(objetivos: list[int]) -> dict[int, list[tuple[str, int]]]:
    res: dict[int, list[tuple[str, int]]] = {t: [] for t in objetivos}
    for a in range(0, len(TEXTO) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", TEXTO, a)
        if h1 & 0xF800 != 0xF000 or h2 & 0xD000 not in (0xD000, 0x9000):
            continue
        s, j1, j2 = h1 >> 10 & 1, h2 >> 13 & 1, h2 >> 11 & 1
        imm = (s << 24) | ((~(j1 ^ s) & 1) << 23) | ((~(j2 ^ s) & 1) << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        t = a + 4 + _sx(imm, 25)
        if t in res:
            res[t].append(("bl" if h2 & 0xD000 == 0xD000 else "b", a))
    return res


def desensambla(a: int, b: int) -> None:
    for i in Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(TEXTO[a:b], a):
        print(f"{i.address:x}: {i.mnemonic} {i.op_str}")


if __name__ == "__main__":
    modo, args = sys.argv[1], sys.argv[2:]
    if modo == "str":
        for m in re.finditer(re.escape(args[0].encode()), RAW[:0xF00000]):
            s = inicio_cadena(m.start())
            print(hex(s), RAW[s : RAW.index(0, s)][:90], [hex(x) for x in xrefs_cadena(s)][:6])
    elif modo == "call":
        for t, v in llamadores([int(x, 16) for x in args]).items():
            print(hex(t), [(k, hex(a)) for k, a in v])
    elif modo == "dis":
        desensambla(int(args[0], 16), int(args[1], 16))
