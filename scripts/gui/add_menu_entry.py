#!/usr/bin/env python3
"""Inserta una entrada nueva en páginas de menú de `viewUnified2.so` (A6000 fw3.21) sin sustituir ninguna (G09 §5d).

Cada página es `CmnViewSettingNode(nodo, hijos**, cuenta, props)` construida en `_INIT_70`: `hijos` = literal PC-relativo
(`ldr r1,[pc]; add r1,pc`) y `cuenta` = `movs r2,#N`. Método: segmento `PT_LOAD` RW añadido al final del fichero con
(1) copia de `.rel.dyn` + relocaciones de los arrays nuevos, (2) los arrays nuevos (una entrada más, con la nueva antes de una
entrada ancla); se reapuntan `DT_REL`/`DT_RELSZ`, el literal y el inmediato de la cuenta. La entrada nueva es
`R_ARM_ABS32` contra un símbolo ya importado (`ref`) con addendum = distancia fija al nodo real dentro del mismo `.so`.
Solo lee/escribe ficheros indicados; no ejecuta nada. Uso: add_menu_entry.py ENTRADA.so SALIDA.so DELTA_HEX
"""
import struct
import sys
from pathlib import Path

R_ARM_ABS32, R_ARM_RELATIVE = 2, 23
ALIGN = 0x8000
# Páginas del A6000 fw3.21 (ELF vaddr): array, cuenta, movs r2,#N, ldr r1 literal, add r1,pc, índice de la entrada ancla (EFCS)
PAGES = (
    (0x4A2F38, 5, 0x166180, 0x166CE8, 0x16618C, 1),
    (0x4A337C, 6, 0x166918, 0x166F70, 0x166924, 4),
    (0x4A3664, 4, 0x166528, 0x166E20, 0x166534, 2),
    (0x4A36C8, 5, 0x16A842, 0x16B16C, 0x16A84A, 1),
    (0x4A3778, 6, 0x168DEC, 0x169200, 0x168DF8, 1),
)
REF_SYMBOL = b"cmnViewSettingNodeRootAelWShutter"


def _segments(d):
    phoff, phnum = struct.unpack_from("<I", d, 28)[0], struct.unpack_from("<H", d, 44)[0]
    return [struct.unpack_from("<8I", d, phoff + 32 * i) for i in range(phnum)]


def _off(segs, va):
    return next(o + va - v for t, o, v, _, fs, _, _, _ in segs if t == 1 and v <= va < v + fs)


def _dynamic(d, segs):
    _, off, _, _, size, *_ = next(s for s in segs if s[0] == 2)
    return off, [struct.unpack_from("<II", d, off + 8 * i) for i in range(size // 8)]


def _symbol_index(d, segs, dyn, name):
    tags = {t: v for t, v in dyn if t}
    symtab, strtab = _off(segs, tags[6]), _off(segs, tags[5])
    for i in range((strtab - symtab) // 16):
        st = struct.unpack_from("<I", d, symtab + 16 * i)[0]
        if d[strtab + st:strtab + st + len(name) + 1] == name + b"\0":
            return i
    raise KeyError(name)


def patch(d: bytes, delta: int) -> bytes:
    segs = _segments(d)
    dyn_off, dyn = _dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = bytearray(d[_off(segs, rel_va):_off(segs, rel_va) + rel_sz])
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    ref_sym = _symbol_index(d, segs, dyn, REF_SYMBOL)

    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + ALIGN - 1) // ALIGN * ALIGN
    new_off = (len(d) + ALIGN - 1) // ALIGN * ALIGN
    extra_rel, blob, out = bytearray(), bytearray(), bytearray(d)
    rel_new_size = rel_sz + 8 * sum(c + 1 for _, c, *_ in PAGES)
    arrays_va = new_va + (rel_new_size + 15) // 16 * 16

    for arr, cnt, movs, lit, add, anchor in PAGES:
        base = _off(segs, arr)
        slots = [struct.unpack_from("<I", d, base + 4 * i)[0] for i in range(cnt)]
        info = [by_off.get(arr + 4 * i) for i in range(cnt)]
        slots.insert(anchor, delta & 0xFFFFFFFF)
        info.insert(anchor, (ref_sym << 8) | R_ARM_ABS32)
        va = arrays_va + len(blob)
        for i, (w, r) in enumerate(zip(slots, info)):
            blob += struct.pack("<I", w)
            if r is not None:
                extra_rel += struct.pack("<II", va + 4 * i, r)
        assert (add + 4 + struct.unpack_from("<I", d, lit)[0]) & 0xFFFFFFFF == arr, "el literal no apunta al array esperado"
        # literal PC-relativo y cuenta (movs r2,#N es 16 bits: 0x2200|N)
        struct.pack_into("<I", out, lit, (va - (add + 4)) & 0xFFFFFFFF)
        assert struct.unpack_from("<H", d, movs)[0] == 0x2200 | cnt, "inmediato de cuenta inesperado"
        struct.pack_into("<H", out, movs, 0x2200 | (cnt + 1))
    rel_new = bytes(rel) + bytes(extra_rel)
    assert len(rel_new) <= rel_new_size
    seg = bytearray(rel_new.ljust(rel_new_size, b"\0")).ljust(arrays_va - new_va, b"\0") + blob

    # tabla de cabeceras nueva (6 entradas) al final del segmento; se mueve e_phoff
    phdr_va = new_va + len(seg)
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, ALIGN]]
    total = len(seg) + 32 * len(new_ph)
    new_ph[-1][4] = new_ph[-1][5] = total
    seg += b"".join(struct.pack("<8I", *s) for s in new_ph)
    out = out.ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(new_ph))
    assert phdr_va > 0
    # DT_REL / DT_RELSZ
    for i, (t, v) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, len(rel_new))
    return bytes(out)


if __name__ == "__main__":
    src, dst, delta = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3], 16)
    dst.write_bytes(patch(src.read_bytes(), delta))
