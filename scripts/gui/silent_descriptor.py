#!/usr/bin/env python3
"""G22 — descriptor propio de «Silent Shooting» en `cmn_view_processDataMgr.so` (A6000 fw3.21), ProcessId 0x12 (inerte).

Copia el descriptor de EFCS (0x46, `@M00F`) a un segmento `PT_LOAD` nuevo y cambia solo lo propio de Silent
(números tomados de la A7S, G22-A): escritura 0x5b, lectura 0x6c, claves 0x291 (set) y 0x293 (get). Las estructuras S2/S3 de EFCS
(listas de valores 1/2) se comparten. Cada puntero copiado conserva su relocación; `D[0x12]` se reapunta al descriptor nuevo.
Solo lee/escribe los ficheros indicados. Uso: silent_descriptor.py ENTRADA.so SALIDA.so
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A

PID_NUEVO, PID_EFCS = 0x12, 0x46
TABLA_D = 0x8C268                    # D[pid]: u32 por ProcessId (process_bindings.py)
DESC_EFCS, DESC_PALABRAS = 0x947F4, 19
MODEL_PALABRAS, S_PALABRAS = 9, 12
C1, C2, CLAVE_SET, CLAVE_GET = 0x5B, 0x6C, 0x291, 0x293
ALIGN = A.ALIGN


def patch(d: bytes) -> bytes:
    segs = A._segments(d)
    dyn_off, dyn = A._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = d[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    word = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))

    desc = list(word(DESC_EFCS, DESC_PALABRAS))
    model_va = desc[6]
    model = list(word(model_va, MODEL_PALABRAS))
    s0_va, s1_va = model[4], model[5]
    s0, s1 = list(word(s0_va, S_PALABRAS)), list(word(s1_va, S_PALABRAS))
    assert (model[2], model[3], s0[0], s1[0]) == (0x54, 0x4F, 0x246, 0x247), (model, s0[:1], s1[:1])
    assert word(TABLA_D + 4 * PID_EFCS)[0] == DESC_EFCS and by_off.get(TABLA_D + 4 * PID_NUEVO) is not None

    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + ALIGN - 1) // ALIGN * ALIGN
    new_off = (len(d) + ALIGN - 1) // ALIGN * ALIGN
    blocks = [("model", model_va, model), ("s0", s0_va, s0), ("s1", s1_va, s1), ("desc", DESC_EFCS, desc)]
    n_rel = sum(1 for _, va, w in blocks for i in range(len(w)) if va + 4 * i in by_off) + 1
    rel_new_size = rel_sz + 8 * n_rel
    data_va = new_va + (rel_new_size + 15) // 16 * 16
    place, cur = {}, data_va
    for name, _, w in blocks:
        place[name] = cur
        cur += (4 * len(w) + 15) // 16 * 16
    model[2], model[3] = C1, C2
    model[4], model[5] = place["s0"], place["s1"]
    s0[0], s1[0] = CLAVE_SET, CLAVE_GET
    desc[6] = place["model"]
    extra, blob = bytearray(), bytearray(cur - data_va)
    for name, src_va, w in blocks:
        for i, x in enumerate(w):
            struct.pack_into("<I", blob, place[name] - data_va + 4 * i, x)
            if src_va + 4 * i in by_off:
                extra += struct.pack("<II", place[name] + 4 * i, by_off[src_va + 4 * i])
    # D[0x12] -> descriptor nuevo (el hueco ya tiene su relocación)
    out = bytearray(d)
    struct.pack_into("<I", out, A._off(segs, TABLA_D + 4 * PID_NUEVO), place["desc"])
    rel_new = bytes(rel) + bytes(extra)
    assert len(rel_new) <= rel_new_size
    seg = bytearray(rel_new.ljust(data_va - new_va, b"\0")) + blob
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, ALIGN]]
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
