#!/usr/bin/env python3
"""Busca tablas `CmnViewMenuItemStruct` (0x28 B/ítem, ver docs/gui/g04) en los .so de vistas (solo lectura).

Heurística: ≥3 ítems seguidos cuyo `+0x0c` es un recurso de texto `0x0204xxxx..0x0206xxxx` con id existente en
`string_english.uxc`. Las tablas contiguas salen fundidas en una sola carrera. Direcciones = vaddr ELF + 0x10000 (base de Ghidra/REA).
Uso: menu_tables.py LIB_DIR STRING_UXC [filtro_nombre]
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import uxc_strings

ITEM = 0x28


def runs(d: bytes, texts: dict, min_items: int = 3):
    """Devuelve [(offset_fichero, n_items)]."""
    def ok(o):
        if o + ITEM > len(d):
            return False
        w = struct.unpack_from("<I", d, o + 0x0C)[0]
        return w >> 16 in (0x204, 0x205, 0x206) and (w & 0xFFFF) in texts

    out, o = [], 0
    while o < len(d) - ITEM:
        if not ok(o):
            o += 4
            continue
        start = o
        while ok(o):
            o += ITEM
        if (o - start) // ITEM >= min_items:
            out.append((start, (o - start) // ITEM))
    return out


if __name__ == "__main__":
    lib_dir, strings = Path(sys.argv[1]), Path(sys.argv[2])
    _, _, texts = uxc_strings.parse(strings.read_bytes())
    for lib in sorted(lib_dir.glob(f"*{sys.argv[3] if len(sys.argv) > 3 else 'view'}*.so")):
        d = lib.read_bytes()
        phoff, n = struct.unpack_from("<I", d, 0x1C)[0], struct.unpack_from("<H", d, 0x2C)[0]
        segs = [struct.unpack_from("<8I", d, phoff + 32 * i) for i in range(n)]
        for off, cnt in runs(d, texts):
            va = next(v + off - po for t, po, v, *_ in segs if t == 1 and po <= off)
            first = texts[struct.unpack_from("<I", d, off + 0x0C)[0] & 0xFFFF][:30]
            print(f"{lib.name}\t{va + 0x10000:#x}\tn={cnt}\t{first!r}")
