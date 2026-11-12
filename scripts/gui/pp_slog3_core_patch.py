#!/usr/bin/env python3
"""G32-C: S-Log3 (gamma `0x17`) toma en el núcleo `av-cam.bin` las ramas por gamma de S-Log2 (`0x14`). NO instala nada.

Tres cambios (G32-C, docs/gui/g32c-slog3-nucleo.md):
- `0x4386783a` `cmp r5,#2` → `#3`: en `0x438677e0` (modo `[+0x193]`=2 con bandera) `0x14…0x17` comparten la rama `0x4386783e`.
- `0x43867924` `blo 0x4386794c` → `blo 0x43867932`: en `0x438678ac` (modo ≠ 1) solo `0x17` llega a ese `blo`; pasa a la clase de S-Log2 (8/9).
- `0x43bc868c` (tabla de clases por gamma, modo 1, entrada `0x17`) `0` → `8`, como `0x14`.
Aditivo: no lo usa todavía ningún constructor del CFW. Uso: pp_slog3_core_patch.py BASE_AVCAM SALIDA
"""
import struct
import sys
from pathlib import Path

BASE = 0x43541000
# (dirección, original, nuevo, qué)
PATCHES = [
    (0x4386783A, bytes.fromhex("022d"), bytes.fromhex("032d"), "0x438677e0: cmp r5,#2 -> #3 (0x14..0x17)"),
    (0x43867924, bytes.fromhex("12d3"), bytes.fromhex("05d3"), "0x438678ac: blo 0x4386794c -> 0x43867932 (0x17 como 0x14)"),
    (0x43BC868C, struct.pack("<I", 0), struct.pack("<I", 8), "tabla 0x43bc8630[0x17]: 0 -> 8 (como 0x14)"),
]


def apply(base: bytes) -> bytes:
    out = bytearray(base)
    for a, old, new, what in PATCHES:
        o = a - BASE
        assert out[o:o + len(old)] == old, (what, out[o:o + len(old)].hex())
        out[o:o + len(new)] = new
    return bytes(out)


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.write_bytes(apply(src.read_bytes()))
    for a, old, new, what in PATCHES:
        print(f"{a:#x}: {old.hex()} -> {new.hex()}  {what}")
