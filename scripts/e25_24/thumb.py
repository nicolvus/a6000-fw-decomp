"""Codificación Thumb-2 mínima para los parches de E25-24 (offline, sin ejecutar firmware).

Solo se implementan las dos ramas que necesitan los parches: `bl` (T1) y `b.w` (T4).
Cada función comprueba alineación y rango; los tests las verifican con Capstone para no
depender de una tabla copiada a mano.
"""
from __future__ import annotations


def _check(addr: int, target: int) -> int:
    if addr % 2 or target % 2:
        raise ValueError("las direcciones Thumb deben ser pares")
    offset = target - (addr + 4)
    if not -(1 << 24) <= offset < (1 << 24):
        raise ValueError(f"destino fuera del alcance de la rama: {addr:#x} -> {target:#x}")
    return offset


def bl(addr: int, target: int) -> bytes:
    """`bl target` ejecutado desde `addr` (Thumb-2 T1, 4 B, ±16 MB)."""
    offset = _check(addr, target)
    s = (offset >> 24) & 1
    i1 = (offset >> 23) & 1
    i2 = (offset >> 22) & 1
    imm10 = (offset >> 12) & 0x3FF
    imm11 = (offset >> 1) & 0x7FF
    j1 = 1 - (i1 ^ s)
    j2 = 1 - (i2 ^ s)
    hw1 = 0xF000 | (s << 10) | imm10
    hw2 = 0xD000 | (j1 << 13) | (j2 << 11) | imm11
    return hw1.to_bytes(2, "little") + hw2.to_bytes(2, "little")


def b_w(addr: int, target: int) -> bytes:
    """`b.w target` ejecutado desde `addr` (Thumb-2 T4, 4 B, ±16 MB)."""
    offset = _check(addr, target)
    s = (offset >> 24) & 1
    i1 = (offset >> 23) & 1
    i2 = (offset >> 22) & 1
    imm10 = (offset >> 12) & 0x3FF
    imm11 = (offset >> 1) & 0x7FF
    j1 = 1 - (i1 ^ s)
    j2 = 1 - (i2 ^ s)
    hw1 = 0xF000 | (s << 10) | imm10
    hw2 = 0x9000 | (j1 << 13) | (j2 << 11) | imm11
    return hw1.to_bytes(2, "little") + hw2.to_bytes(2, "little")


NOP = b"\x00\xbf"
