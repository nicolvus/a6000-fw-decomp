#!/usr/bin/env python3
"""G28 — amplía el espacio de ProcessIds de la copia del gestor de procesos que lleva `viewUnified2.so` (A6000 fw3.21) y le añade descriptores propios.

Por qué: de los 233 ProcessIds (0…0xE8) 230 los usa algún nodo de `CautionConfig` (Custom Key, Function Menu Set., …); prestarlos para Picture Profile rompe esos menús
(3.62). Aquí los ajustes de PP van en pids NUEVOS (`0xE9…`) y no se toca ningún pid existente.
Qué se cambia (todo en `viewUnified2.so`; el gestor real de la UI es esa copia, no `cmn_view_processDataMgr.so`):
  · tres comprobaciones `pid ≤ 0xE8` (`getElement` 0x1b4568, `initProcessDataElement` 0x25d8f2, `setProcessId` 0x25d91c): se sustituyen por un `b.w` a un tramo
    nuevo que compara con `PID_MAX` (el `cmp rN,#imm8` de 2 B no admite más de 255) y vuelve;
  · las dos tablas (pid→caso de factoría `ELEM`, pid→descriptor `D`) se copian a un segmento nuevo con `PID_MAX+1` entradas; los tres literales PC-relativos que las
    apuntaban se reapuntan (los pids nuevos usan el caso de `Normal`, la única clase que usa el descriptor);
  · un descriptor `Normal` por ajuste (`pp_descriptors.Ajuste`) con las mismas estructuras que `pp_descriptors.patch` y sin respaldo NVRAM, vista de destino ni inhibiciones.
El segmento es RWX (lleva código, tablas y relocaciones RELATIVE de los punteros nuevos). Uso: pid_space.py ENTRADA.so SALIDA.so
"""
import struct
import sys
from pathlib import Path

from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import pp_descriptors as P

N_ORIG = 0xE9                                   # entradas de las tablas originales
PID_MAX = 0x110                                 # último pid admitido; 0x110 = 0x88 << 1 cabe en el inmediato modificado de `cmp.w`
PID_PRIMERO = N_ORIG                            # primer pid nuevo
ELEM, D = 0x3A5E1C, 0x4457D4                    # tablas originales (VA)
REF_NORMAL, PID_M00B = 0x12, 0x3F               # pid de clase Normal · pid con descriptor «@M00B» (nombre del modelo)
# (dirección del cmp+bhi/cmp+push, bytes originales, literal PC-relativo, valor original del literal, tabla, pc del add)
SITIO_GET = (0x1B4568, bytes.fromhex("e829f8b5"), 0x1B4598, ELEM - 0x1B457E)             # cmp r1,#0xe8 ; push {r3-r7,lr}
SITIO_INIT = (0x25D8F2, bytes.fromhex("e82a0ad8"), 0x25D910, D - 0x25D8FE)               # cmp r2,#0xe8 ; bhi 0x25d90c
SITIO_SET = (0x25D91C, bytes.fromhex("e82909d8"), 0x25D938, D - 0x25D928)  # cmp r1,#0xe8 ; bhi 0x25d934
CODIGO_RESERVA = 0x80


def _asm(src: str, addr: int) -> bytes:
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, addr)
    return bytes(enc)


def tramos(code_va: int) -> tuple[bytes, dict[int, int]]:
    """Código de los tres tramos (concatenado) y su dirección: {sitio: dirección del tramo}."""
    s_get, s_init, s_set = code_va, code_va + 0x20, code_va + 0x40
    cod = bytearray(CODIGO_RESERVA)
    for va, src in ((s_get, f"cmp.w r1,#{PID_MAX:#x}; push {{r3,r4,r5,r6,r7,lr}}; b.w {SITIO_GET[0] + 4:#x}"),
                    (s_init, f"cmp.w r2,#{PID_MAX:#x}; bls ok; b.w 0x25d90c; ok: b.w 0x25d8f6"),
                    (s_set, f"cmp.w r1,#{PID_MAX:#x}; bls ok; b.w 0x25d934; ok: b.w 0x25d920")):
        b = _asm(src, va)
        assert len(b) <= 0x20, src
        cod[va - code_va:va - code_va + len(b)] = b
    return bytes(cod), {SITIO_GET[0]: s_get, SITIO_INIT[0]: s_init, SITIO_SET[0]: s_set}


def patch(d: bytes, ajustes) -> bytes:
    segs = A._segments(d)
    dyn_off, dyn = A._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = d[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    word = lambda va, n=1: struct.unpack_from(f"<{n}I", d, A._off(segs, va))
    n_new = PID_MAX + 1
    assert len({a.pid for a in ajustes}) == len(ajustes) and all(PID_PRIMERO <= a.pid <= PID_MAX for a in ajustes), "pid fuera del espacio nuevo"
    for va, orig, lit, valor in (SITIO_GET, SITIO_INIT, SITIO_SET):
        assert d[va:va + 4] == orig and word(lit)[0] == valor, f"sitio {va:#x} inesperado"

    elem = list(word(ELEM, N_ORIG))
    normal = elem[REF_NORMAL]
    assert elem[0x46] == normal, "la tabla de clases no es la esperada"
    ref_model_va = word(word(D + 4 * PID_M00B)[0], P.DESC_PALABRAS)[6]
    name_va, name_rel = word(ref_model_va)[0], by_off[ref_model_va]
    assert name_rel & 0xFF == 0x17 and d[A._off(segs, name_va):A._off(segs, name_va) + 6] == b"@M00B\0"
    d_old = list(word(D, N_ORIG))
    d_rel_old = {i: by_off[D + 4 * i] for i in range(N_ORIG) if D + 4 * i in by_off}
    assert len(d_rel_old) == N_ORIG, "alguna entrada de D no lleva relocación"

    n_rel = N_ORIG + len(ajustes) * (P.DESC_PALABRAS + 8)
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(d) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    rel_new_size = rel_sz + 8 * n_rel
    code_va = new_va + (rel_new_size + 15) // 16 * 16
    elem_va = code_va + CODIGO_RESERVA
    d_va = elem_va + 4 * n_new
    data_va = d_va + 4 * n_new
    cod, hooks = tramos(code_va)

    blob, extra = bytearray(), bytearray()

    def alloc(words, relmap=None):
        va = data_va + len(blob)
        blob.extend(struct.pack(f"<{len(words)}I", *words))
        blob.extend(b"\0" * (-len(blob) % 16))
        for i, r in (relmap or {}).items():
            extra.extend(struct.pack("<II", va + 4 * i, r))
        return va

    d_new = d_old + [0] * (n_new - N_ORIG)
    for i, r in d_rel_old.items():                                   # las entradas antiguas conservan su relocación en la tabla nueva
        extra.extend(struct.pack("<II", d_va + 4 * i, r))
    for a in ajustes:
        n = len(a.valores)
        assert 0 < n < 256
        s, g, t = alloc([a.clave]), alloc([a.clave + 2 if a.clave_get is None else a.clave_get]), alloc([1])
        v = alloc([x & 0xFFFFFFFF for x in a.valores])
        c = alloc([P.NADA] * n)
        m = alloc([name_va, 1, a.evento, a.id_get, s, g, t, v, 1 | (n << 8)], {0: name_rel, 4: 0x17, 5: 0x17, 6: 0x17, 7: 0x17})
        desc = [P.NADA, c, 0, 0, 0, n << 8, m, 1, 0, 0, 0, 0xFFFFFFFF, 0, 0, 0, 0, 0, 0, 0]
        d_new[a.pid] = alloc(desc, {1: 0x17, 6: 0x17})
        extra.extend(struct.pack("<II", d_va + 4 * a.pid, 0x17))
    elem_new = elem + [normal] * (n_new - N_ORIG)
    tablas = struct.pack(f"<{n_new}I", *elem_new) + struct.pack(f"<{n_new}I", *d_new)
    assert len(rel) + len(extra) <= rel_new_size

    out = bytearray(d)
    for va, orig, lit, _ in (SITIO_GET, SITIO_INIT, SITIO_SET):                 # ganchos y literales (código: el VA del primer LOAD es el offset)
        out[va:va + 4] = _asm(f"b.w {hooks[va]:#x}", va)
    struct.pack_into("<I", out, SITIO_GET[2], (elem_va - 0x1B457E) & 0xFFFFFFFF)
    struct.pack_into("<I", out, SITIO_INIT[2], (d_va - 0x25D8FE) & 0xFFFFFFFF)
    struct.pack_into("<I", out, SITIO_SET[2], (d_va - 0x25D928) & 0xFFFFFFFF)
    rel_new = bytes(rel) + bytes(extra)
    seg = bytearray(rel_new.ljust(code_va - new_va, b"\0")) + cod + tablas + blob
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 7, A.ALIGN]]      # RWX
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


if __name__ == "__main__":
    import pp_menu_spec as M
    aj = [P.Ajuste(M.PIDS[i], s.clave, tuple(v for _, v in s.opciones), s.evento, s.id_get, s.clave_get) for i, s in enumerate(M.SETTINGS.values())]
    Path(sys.argv[2]).write_bytes(patch(Path(sys.argv[1]).read_bytes(), aj))
