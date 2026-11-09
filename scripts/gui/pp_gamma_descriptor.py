#!/usr/bin/env python3
"""G23 — descriptor de Gamma (Picture Profile) en `cmn_view_processDataMgr.so` (A6000 fw3.21), ProcessId 0x3c (LocalAreaLimitation, inerte).

Layout verificado por desensamblado de `CmnViewProcessDataElementNormal::getDataModel*` (G23 §Layout):
  desc +0x04 cautions por opción · +0x15 nº de opciones · +0x18 modelo · +0x1c nº de modelos
  modelo +0 nombre · +4 update · +8 evento de escritura · +0xc id de lectura · +0x10 claves de escritura · +0x14 claves de lectura
         +0x18 tipos (1 = número) · +0x1c tabla opción→valor [opción·nclaves + clave] · +0x20 nclaves · +0x21 nº de entradas de la tabla
Escritura `@M00B` 0x40 clave 0x214; lectura `model/CAMERA` 0x49 clave 0x216 (G19 §2b). Valores de la A6000 (G20 §1).
Uso: pp_gamma_descriptor.py ENTRADA.so SALIDA.so
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A

PID = 0x3C
TABLA_D = 0x8C268
DESC_PALABRAS, MODEL_PALABRAS = 19, 9
PID_M00B = 0x3F                       # descriptor real con "@M00B": de él se copia el puntero al nombre
EVENTO_SET, ID_GET, CLAVE_SET, CLAVE_GET = 0x40, 0x49, 0x214, 0x216
GAMMAS = (4, 5, 3, 6, 7, 8, 9)         # Movie, Still, ITU709, Cine1–4 (orden del menú)
NADA = 0xA45                            # relleno de caution que usa el descriptor inerte


def patch(d: bytes) -> bytes:
    segs = A._segments(d)
    dyn_off, dyn = A._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = d[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    word = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))

    desc_va = word(TABLA_D + 4 * PID)[0]
    desc = list(word(desc_va, DESC_PALABRAS))
    assert desc[6] == 0 and desc[5] & 0xFF00 and by_off.get(TABLA_D + 4 * PID) is not None, "el pid 0x3c ya no es inerte"
    m00b = word(word(word(TABLA_D + 4 * PID_M00B)[0], DESC_PALABRAS)[6], MODEL_PALABRAS)
    name_va, name_rel = m00b[0], None
    ref_model_va = word(word(TABLA_D + 4 * PID_M00B)[0], DESC_PALABRAS)[6]
    name_rel = by_off[ref_model_va]
    assert name_rel & 0xFF == 0x17 and d[A._off(segs, name_va):A._off(segs, name_va) + 6] == b"@M00B\0"

    n = len(GAMMAS)
    # bloques nuevos: (nombre, palabras, índices que son punteros)
    model = [name_va, 1, EVENTO_SET, ID_GET, 0, 0, 0, 0, 1 | (n << 8)]
    blocks = {
        "set": [CLAVE_SET], "get": [CLAVE_GET], "tipos": [1],
        "valores": list(GAMMAS), "caut": [NADA] * n, "model": model, "desc": desc,
    }
    ptrs = {"model": {0: None, 4: "set", 5: "get", 6: "tipos", 7: "valores"}, "desc": {1: "caut", 6: "model"}}

    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(d) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    n_rel = sum(len(p) for p in ptrs.values())          # model[0] hereda relocación y el resto son nuevas
    rel_new_size = rel_sz + 8 * n_rel
    data_va = new_va + (rel_new_size + 15) // 16 * 16
    place, cur = {}, data_va
    for k, w in blocks.items():
        place[k] = cur
        cur += (4 * len(w) + 15) // 16 * 16
    for blk, mp in ptrs.items():
        for i, tgt in mp.items():
            if tgt:
                blocks[blk][i] = place[tgt]
    desc[5] = (desc[5] & ~0xFF00) | (n << 8)
    desc[7] = 1                                          # nº de modelos (la plantilla inerte trae 0)
    extra, blob = bytearray(), bytearray(cur - data_va)
    for k, w in blocks.items():
        for i, x in enumerate(w):
            struct.pack_into("<I", blob, place[k] - data_va + 4 * i, x)
        for i in ptrs.get(k, {}):
            extra += struct.pack("<II", place[k] + 4 * i, name_rel if k == "model" and i == 0 else 0x17)
    out = bytearray(d)
    struct.pack_into("<I", out, A._off(segs, TABLA_D + 4 * PID), place["desc"])
    rel_new = bytes(rel) + bytes(extra)
    assert len(rel_new) <= rel_new_size
    seg = bytearray(rel_new.ljust(data_va - new_va, b"\0")) + blob
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    total = len(seg) + 32 * len(new_ph)
    new_ph[-1][4] = new_ph[-1][5] = total
    seg += b"".join(struct.pack("<8I", *s) for s in new_ph)
    out = out.ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(new_ph))
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, len(rel_new))
    return bytes(out)


if __name__ == "__main__":
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes()))
