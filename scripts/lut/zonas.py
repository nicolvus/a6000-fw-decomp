#!/usr/bin/env python3
"""Escáner de referencias a una zona de `av-cam`: literales que caen dentro y direcciones PC-relativas (`adr`, `ldr rX,[pc,#i]` + `add rX, pc`)
que apuntan a ella. Sirve para decidir si un hueco es realmente libre (G107 §3, G116).
Límite: no ve `movw`/`movt` absolutos, tablas de saltos ni punteros calculados en tiempo de ejecución; úsalo como filtro, no como prueba única.
Uso: `zonas.py LO HI` (direcciones virtuales en hex) imprime las referencias de `av-cam.bin`.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
import avcam_dinamico as D

BASE = D.BASE


def _u16(img: bytes, o: int) -> int:
    return struct.unpack_from("<H", img, o)[0]


def _u32(img: bytes, o: int) -> int | None:
    return struct.unpack_from("<I", img, o)[0] if 0 <= o <= len(img) - 4 else None


def literales(img: bytes, lo: int, hi: int, base: int = BASE) -> list[tuple[int, int]]:
    """(dirección del literal, valor) de las palabras alineadas a 4 que caen en `[lo, hi)`."""
    return [(base + o, v) for o in range(0, len(img) - 3, 4) if lo <= (v := _u32(img, o)) < hi]


def referencias(img: bytes, lo: int, hi: int, base: int = BASE) -> list[tuple[int, str, int]]:
    """(dirección de la instrucción, tipo, destino) de las referencias PC-relativas que caen en `[lo, hi)`.
    Tipos: `adr` (`add rD, pc, #i`), `ldr+add` (literal + `add rD, pc` con el mismo registro) y `literal`."""
    from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs
    from capstone.arm import ARM_OP_MEM, ARM_OP_REG, ARM_REG_PC

    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    a4 = lambda a: a & ~3
    dentro = lambda t: lo <= t < hi
    hits = [(a, "literal", v) for a, v in literales(img, lo, hi, base)]

    for o in range(0, len(img) - 3, 2):                       # `adr` (T1): 10100 rD imm8, destino = align4(pc)+imm·4
        if not 0xA000 <= (w := _u16(img, o)) <= 0xA7FF:
            continue
        t = a4(base + o + 4) + (w & 0xFF) * 4
        if dentro(t) and (base + o, "adr", t) not in hits:
            hits.append((base + o, "adr", t))

    adr_pc = lambda w: 0x4478 <= w <= 0x447F or 0x44F8 <= w <= 0x44FF   # add rD, pc (T1)
    for o in range(2, len(img) - 2, 2):
        if not adr_pc(_u16(img, o)):
            continue
        for atras in (2, 4):                                   # la instrucción anterior puede medir 2 o 4 bytes
            ini = o - atras
            ins = list(md.disasm(img[ini:o + 6], base + ini))
            if len(ins) < 2 or ins[1].address != base + o or ins[0].mnemonic != "ldr" or len(ins[0].operands) != 2:
                continue
            mem, reg = ins[0].operands[1], ins[0].operands[0]
            if mem.type != ARM_OP_MEM or mem.mem.base != ARM_REG_PC or reg.type != ARM_OP_REG:
                continue
            if ins[1].mnemonic != "add" or len(ins[1].operands) != 2:
                continue
            if ins[1].operands[1].type != ARM_OP_REG or ins[1].operands[1].reg != ARM_REG_PC:
                continue
            if ins[1].operands[0].reg != reg.reg:
                continue
            lit = _u32(img, a4(ins[0].address + 4) + mem.mem.disp - base)
            if lit is None:
                continue
            t = (lit + a4(ins[1].address + 4)) & 0xFFFFFFFF
            if dentro(t):
                hits.append((ins[1].address, "ldr+add", t))
    return sorted(set(hits))


def libre(img: bytes, zona: tuple[int, int], base: int = BASE) -> tuple[bool, list[tuple[int, str, int]]]:
    """(¿sin referencias?, lista). Complemento de `apply_bytes` (que además exige los bytes a cero)."""
    refs = referencias(img, *zona, base)
    return not refs, refs


if __name__ == "__main__":
    img = D.C.BIN.read_bytes() if hasattr(D, "C") else (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
    a, b = (int(x, 16) for x in sys.argv[1:3])
    for ref in referencias(img, a, b):
        print(f"{ref[0]:#010x} {ref[1]:8s} -> {ref[2]:#010x}")
