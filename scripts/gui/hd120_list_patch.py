#!/usr/bin/env python3
"""G70-HD120 — «100p 50M» y «120p 50M» al final de la lista Ajuste grabación de la A6000 (fw3.21). Solo escribe una copia de `CautionConfig.so`.

`CmnViewSettingNodeMovieRecordingSetting::_getSubNode` (+0x108e71) elige por tipo de modelo; el tipo 29 (A6000) usa `…SettingType04` (17 nodos). Sin quitar
nada: se añade un segmento PT_LOAD RW (patrón de add_menu_entry.py) con la copia de `.rel.dyn`, 19 punteros (los 17 de Type04 + los nodos 100p y 120p, cada uno
con su relocalización ABS32 contra el símbolo exportado) y la tabla de cabeceras nueva; el símbolo exportado `…Type04` pasa a apuntar a ese array y la celda
`NumOf…Type04` (en su sitio) pasa de 17 a 19. `_getSubNode` no cambia: resuelve el símbolo por GOT. Type04 solo lo usa el tipo 29.
Uso: hd120_list_patch.py ENTRADA.so SALIDA.so   (valida los bytes originales; idempotente sobre el resultado)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as ame

R_ARM_ABS32 = 2
ALIGN = ame.ALIGN
SYM_LIST, SYM_COUNT = b"cmnViewSettingNodesMovieRecordingSettingType04", b"cmnViewSettingNodesNumOfMovieRecordingSettingType04"
NEW_NODES = (b"cmnViewSettingNodeMovieRecordingSetting100_p_50M", b"cmnViewSettingNodeMovieRecordingSetting120_p_50M")
OLD_N = 17


def _sym_ent(d, symtab, i):
    return symtab + 16 * i


def patch(d: bytes) -> bytes:
    segs = ame._segments(d)
    dyn_off, dyn = ame._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    symtab = ame._off(segs, tags[6])
    i_list, i_cnt = ame._symbol_index(d, segs, dyn, SYM_LIST), ame._symbol_index(d, segs, dyn, SYM_COUNT)
    i_new = [ame._symbol_index(d, segs, dyn, n) for n in NEW_NODES]
    _, l_val, l_size = struct.unpack_from("<III", d, _sym_ent(d, symtab, i_list))
    c_val = struct.unpack_from("<I", d, _sym_ent(d, symtab, i_cnt) + 4)[0]
    cnt_off = ame._off(segs, c_val)
    cnt = struct.unpack_from("<I", d, cnt_off)[0]
    if cnt == OLD_N + 2 and l_size == 4 * (OLD_N + 2):
        return d
    assert (cnt, l_size) == (OLD_N, 4 * OLD_N), f"lista/cuenta inesperadas {cnt} {l_size}"

    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = d[ame._off(segs, rel_va):ame._off(segs, rel_va) + rel_sz]
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    info = [by_off[l_val + 4 * i] for i in range(OLD_N)]
    assert all(x & 0xFF == R_ARM_ABS32 for x in info), "los punteros de Type04 deben ser ABS32 contra símbolo"
    assert all(struct.unpack_from("<I", d, ame._off(segs, l_val) + 4 * i)[0] == 0 for i in range(OLD_N)), "addendum en sitio distinto de 0"
    info += [(i << 8) | R_ARM_ABS32 for i in i_new]

    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + ALIGN - 1) // ALIGN * ALIGN
    new_off = (len(d) + ALIGN - 1) // ALIGN * ALIGN
    n = OLD_N + 2
    rel_new_size = rel_sz + 8 * n
    arr_va = new_va + (rel_new_size + 15) // 16 * 16
    extra = b"".join(struct.pack("<II", arr_va + 4 * i, r) for i, r in enumerate(info))
    seg = bytearray((rel + extra).ljust(arr_va - new_va, b"\0")) + bytes(4 * n)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, ALIGN]]
    total = len(seg) + 32 * len(new_ph)
    new_ph[-1][4] = new_ph[-1][5] = total
    phdr_off = new_off + len(seg)
    seg += b"".join(struct.pack("<8I", *s) for s in new_ph)

    out = bytearray(d).ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(new_ph))
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, rel_sz + len(extra))
    struct.pack_into("<I", out, _sym_ent(d, symtab, i_list) + 4, arr_va)
    struct.pack_into("<I", out, _sym_ent(d, symtab, i_list) + 8, 4 * n)
    struct.pack_into("<I", out, cnt_off, n)
    return bytes(out)


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.write_bytes(patch(src.read_bytes()))
    print("ok", dst)
