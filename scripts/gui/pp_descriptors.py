#!/usr/bin/env python3
"""G23/G28 — descriptores de Picture Profile (A6000 fw3.21): uno por ProcessId inerte, todos en un único PT_LOAD añadido.

G28: la UI NO carga `cmn_view_processDataMgr.so`; usa la copia estática del gestor que lleva `viewUnified2.so` (`TABLA_D_VU2`, tabla pid→clase `ELEM_VU2`). `patch(..., tabla_d=TABLA_D_VU2)` y `clase_normal` actúan sobre ella.

Layout (desensamblado de `CmnViewProcessDataElementNormal::getDataModel*`, G23): desc +0x04 cautions por opción · +0x15 nº de opciones · +0x18 modelo · +0x1c nº de modelos;
modelo +0 nombre · +4 update · +8 evento de escritura · +0xc id de lectura · +0x10 claves de escritura · +0x14 de lectura · +0x18 tipos (1 = número) ·
+0x1c tabla opción→valor · +0x20 nclaves · +0x21 nº de entradas. Escritura `@M00B` 0x40 clave `0x1f8+4·i`; lectura `model/CAMERA` 0x49 clave +2 (G19 §2b/§2c).
Un ajuste = `Ajuste(pid, clave, valores)`; el valor de la opción k es `valores[k]` (entero con signo).
"""
import struct
from dataclasses import dataclass

import add_menu_entry as A

TABLA_D = 0x8C268                     # cmn_view_processDataMgr.so (NO la usa la UI, G28)
TABLA_D_VU2, ELEM_VU2, REF_NORMAL = 0x4457D4, 0x3A5E1C, 0x12   # viewUnified2.so: D[pid] · tabla pid→caso de factoría (u32, en el segmento de código) · pid de clase Normal
DESC_PALABRAS, MODEL_PALABRAS = 19, 9
PID_M00B = 0x3F                       # descriptor real con "@M00B": de él se copia el puntero al nombre
EVENTO_SET, ID_GET = 0x40, 0x49
NADA = 0xA45                          # relleno de caution del descriptor inerte


@dataclass(frozen=True)
class Ajuste:
    pid: int
    clave: int                        # clave de escritura (0x1f8 + 4·i); la de lectura es clave + 2
    valores: tuple
    evento: int = EVENTO_SET
    id_get: int = ID_GET
    clave_get: int | None = None      # por defecto clave + 2


def clase_normal(d: bytes, pids, elem: int = ELEM_VU2) -> bytes:
    """Fuerza la clase `Normal` (la única que usa el descriptor) en los `pids`: `getElement` indexa `elem[pid]` → caso de la factoría; 16 de los pids de PP eran `Custom*Button`."""
    out, normal = bytearray(d), struct.unpack_from("<I", d, elem + 4 * REF_NORMAL)[0]
    assert struct.unpack_from("<I", d, elem + 4 * 0x46)[0] == normal, "la tabla de clases no es la esperada"
    for pid in pids:
        struct.pack_into("<I", out, elem + 4 * pid, normal)
    return bytes(out)


def patch(d: bytes, ajustes, tabla_d: int = TABLA_D) -> bytes:
    segs = A._segments(d)
    dyn_off, dyn = A._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = d[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    word = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))
    ref_model_va = word(word(tabla_d + 4 * PID_M00B)[0], DESC_PALABRAS)[6]
    name_va, name_rel = word(ref_model_va)[0], by_off[ref_model_va]
    assert name_rel & 0xFF == 0x17 and d[A._off(segs, name_va):A._off(segs, name_va) + 6] == b"@M00B\0"
    assert len({a.pid for a in ajustes}) == len(ajustes)

    plan, n_rel, cur_words = [], 0, 0
    for a in ajustes:
        desc_va = word(tabla_d + 4 * a.pid)[0]
        desc = list(word(desc_va, DESC_PALABRAS))
        assert desc[6] == 0 and desc[5] & 0xFF00 and by_off.get(tabla_d + 4 * a.pid) is not None, f"el pid {a.pid:#x} no es inerte"
        n = len(a.valores)
        assert 0 < n < 256
        n_rel += 7 + DESC_PALABRAS
        # G28: los punteros del descriptor original llevan relocación; hay que conservarla en la copia (sin ella apuntan a la dirección de enlace, no a la de carga)
        punteros = {i: by_off[desc_va + 4 * i] for i in range(DESC_PALABRAS) if desc_va + 4 * i in by_off}
        plan.append((a, desc, n, punteros))
        cur_words += 4 * (1 + 1 + 1 + n + n) + 4 * (MODEL_PALABRAS + DESC_PALABRAS) + 5 * 16
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(d) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    rel_new_size = rel_sz + 8 * n_rel
    data_va = new_va + (rel_new_size + 15) // 16 * 16
    blob, extra, out = bytearray(), bytearray(), bytearray(d)

    def alloc(words, relmap=None):
        va = data_va + len(blob)
        blob.extend(struct.pack(f"<{len(words)}I", *words))
        blob.extend(b"\0" * (-len(blob) % 16))
        for i, r in (relmap or {}).items():
            extra.extend(struct.pack("<II", va + 4 * i, r))
        return va

    for a, desc, n, punteros in plan:
        s, g, t = alloc([a.clave]), alloc([a.clave + 2 if a.clave_get is None else a.clave_get]), alloc([1])
        v = alloc([x & 0xFFFFFFFF for x in a.valores])
        c = alloc([NADA] * n)
        m = alloc([name_va, 1, a.evento, a.id_get, s, g, t, v, 1 | (n << 8)], {0: name_rel, 4: 0x17, 5: 0x17, 6: 0x17, 7: 0x17})
        desc[5] = (desc[5] & ~0xFF00) | (n << 8)
        desc[7] = 1
        desc[1], desc[6] = c, m
        # el pid prestado es una función real: su respaldo NVRAM (palabras 8-9) y su vista de destino (10) no son de PP; escribirían en ajustes ajenos
        for i in (8, 9, 10):
            desc[i] = 0
            punteros.pop(i, None)
        dv = alloc(desc, {**punteros, 1: 0x17, 6: 0x17})
        struct.pack_into("<I", out, A._off(segs, tabla_d + 4 * a.pid), dv)       # D[pid] ya tenía su relocación
    rel_new = bytes(rel) + bytes(extra)
    assert len(rel_new) <= rel_new_size
    seg = bytearray(rel_new.ljust(data_va - new_va, b"\0")) + blob
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    new_ph[-1][4] = new_ph[-1][5] = len(seg) + 32 * len(new_ph)
    seg += b"".join(struct.pack("<8I", *s) for s in new_ph)
    out = out.ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(new_ph))
    for i, (tg, _) in enumerate(dyn):
        if tg == 0x11:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, new_va)
        if tg == 0x12:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, len(rel_new))
    return bytes(out)
