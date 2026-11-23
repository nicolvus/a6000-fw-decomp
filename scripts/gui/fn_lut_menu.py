#!/usr/bin/env python3
"""G86 — opción «LUT» en el menú Fn (lado `viewUnified4.so`): el nodo de ajuste «LUT» (el de la carpeta CFW, mismo pid/Backup) pasa a ser un hijo más de la raíz de
la franja Fn, con la vista nativa de opciones (título, fila ◄ ► con la actual resaltada, valor en la casilla).

Mecanismo (VERIFICADO en bytes del 3.21, ver docs/gui/g86-menu-fn-lut.md):
  * La vista `FNMENU` guarda por ranura `[this+0x258+8k]` = valor de Backup de la asignación y `[this+0x25c+8k]` = nº de serie (SRNum) del hijo de la raíz Fn
    (`CmnViewSettingNode` de 38 hijos, `0x1bb940`, hijos en `0x1b0d28`); el paso valor→SRNum es un `tbh` de 0x30 casos en `0xdd078`.
  * Se añade un hijo 39 (SRNum 39 = `0x27`) con el nodo «LUT» y el valor de asignación `0x26` (hasta ahora «por defecto», sin efecto) → SRNum `0x27`.
  * Sin hueco de código en alcance del `tbh`, los 18 bloques contiguos de 8 B se recompactan a 4 B + un cuerpo común: caben hasta 16 bloques nuevos de 4 B.
  * G102: varios hijos (39…), uno por nodo, con los valores libres `VALORES` en orden.
Lista de asignación de las 12 ranuras y tabla opción→valor (que lleva a `0x26`): `fn_lut_listas.py` (G86-B); el valor guardado NO es el `0xf` de la opción sino `tabla[0xf]`.
shortcut: el nodo es una copia de datos del de la carpeta CFW (mismo pid), no el mismo objeto; ambos leen/escriben el mismo Backup.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A

TBH, TBH_N = 0xDD07C, 0x30                     # tabla de saltos valor-de-asignación → bloque (u16, destino = TBH + 2·u16)
FIN = 0xDD236                                  # `str.w r3,[r4,#0x25c]` común a los bloques
BLOQUES = 0xDD0FE                              # 18 bloques contiguos de 8 B (`add.w r4,r4,r5,lsl #3; movs r3,#N; b.n FIN`), 0xdd0fe…0xdd18e
N_BLOQUES = 18
VALOR_LUT, SRNUM_LUT = 0x26, 0x27
VALORES = (0x26, 0x27, 0x28, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x23)   # G102: valores de asignación que el `tbh` mandaba al «por defecto» (0xdd23a); el k-ésimo → SRNum 0x27 + k
TABLA_VA, TABLA_N = 0x1B0D28, 38               # hijos de la raíz Fn
LIT_LDR, LIT_ADD, MOVS_N = 0xE0BA6, 0xE0BAE, 0xE0BAA   # `ldr r1,[pc,#0xbc]; … add r1,pc` del ctor y `movs r2,#0x26`
REF = b"cmnViewSettingNodeRootMemoryRecallFn"  # símbolo ya importado de CautionConfig; el hijo nuevo = REF + delta


def _asm(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def _bloques(data: bytes, n: int) -> tuple[dict[int, int], bytes]:
    """Recompacta los `N_BLOQUES` bloques: (mapa dirección vieja → nueva, bytes nuevos). Nuevos: `movs r3,#N; b.n común` por bloque original, uno por hijo nuevo
    (SRNum 0x27 + k) y el cuerpo común (`add.w r4,r4,r5,lsl #3; b.n FIN`)."""
    srn = []
    for i in range(N_BLOQUES):
        a = BLOQUES + 8 * i
        m = data[a + 4]
        if data[a + 5] != 0x23 or data[a:a + 8] != _asm(f"add.w r4, r4, r5, lsl #3; movs r3, #{m}; b.n {FIN:#x}", a):
            raise ValueError(f"bloque {a:#x} distinto del 3.21 (¿ya parcheado?)")
        srn.append(m)
    srn += [SRNUM_LUT + k for k in range(n)]
    comun = BLOQUES + 4 * len(srn)
    nuevo = b"".join(_asm(f"movs r3, #{m}; b.n {comun:#x}", BLOQUES + 4 * i) for i, m in enumerate(srn))
    nuevo += _asm(f"add.w r4, r4, r5, lsl #3; b.n {FIN:#x}", comun)
    if len(nuevo) > 8 * N_BLOQUES:
        raise ValueError(f"{n} hijos nuevos no caben en el hueco de los bloques")
    return {BLOQUES + 8 * i: BLOQUES + 4 * i for i in range(N_BLOQUES)}, nuevo + b"\x00\xbf" * ((8 * N_BLOQUES - len(nuevo)) // 2)


def _entrada(valor: int, destino: int) -> tuple[int, int]:
    return TBH + 2 * valor, (destino - TBH) // 2


def patch_vu4(data: bytes, deltas) -> bytes:
    """`deltas` = [VA de cada nodo nuevo en CautionConfig − VA de `cmnViewSettingNodeRootMemoryRecallFn`] (distancia fija dentro de esa biblioteca); un entero = un nodo.
    El k-ésimo nodo es el hijo 39 + k de la raíz Fn y lo abre el valor de asignación `VALORES[k]`."""
    deltas = [deltas] if isinstance(deltas, int) else list(deltas)
    n = len(deltas)
    if not 1 <= n <= len(VALORES):
        raise ValueError(f"entre 1 y {len(VALORES)} nodos")
    out = bytearray(data)
    mapa, nuevo = _bloques(data, n)
    actual = {v: TBH + 2 * struct.unpack_from("<H", data, TBH + 2 * v)[0] for v in range(TBH_N)}
    for v in VALORES[:n]:
        if actual[v] != 0xDD23A:
            raise ValueError(f"el valor {v:#x} ya tiene bloque")
    out[BLOQUES:BLOQUES + 8 * N_BLOQUES] = nuevo
    for v, dst in actual.items():
        if dst in mapa:
            a, u = _entrada(v, mapa[dst])
            struct.pack_into("<H", out, a, u)
    for k, v in enumerate(VALORES[:n]):
        a, u = _entrada(v, BLOQUES + 4 * (N_BLOQUES + k))
        struct.pack_into("<H", out, a, u)

    segs = A._segments(data)
    dyn_off, dyn = A._dynamic(data, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = bytearray(data[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz])
    by_off = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, rel_sz, 8)}
    ref_sym = A._symbol_index(data, segs, dyn, REF)
    base = A._off(segs, TABLA_VA)
    slots = [struct.unpack_from("<I", data, base + 4 * i)[0] for i in range(TABLA_N)]
    info = [by_off.get(TABLA_VA + 4 * i) for i in range(TABLA_N)]
    assert all(i is not None for i in info), "los 38 hijos deben ir relocados"
    slots += [d & 0xFFFFFFFF for d in deltas]
    info += [(ref_sym << 8) | A.R_ARM_ABS32] * n

    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(data) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    rel_new_size = rel_sz + 8 * len(slots)
    arr_va = new_va + (rel_new_size + 15) // 16 * 16
    extra = b"".join(struct.pack("<II", arr_va + 4 * i, r) for i, r in enumerate(info))
    rel_new = bytes(rel) + extra
    seg = bytearray(rel_new.ljust(arr_va - new_va, b"\0")) + b"".join(struct.pack("<I", w) for w in slots)

    # literal PC-relativo del ctor (`ldr r1,[pc,#0xbc]` + `add r1,pc`) y cuenta (`movs r2,#38`)
    lit = ((LIT_LDR + 4) & ~3) + 0xBC
    assert (struct.unpack_from("<I", data, lit)[0] + LIT_ADD + 4) & 0xFFFFFFFF == TABLA_VA, "el literal no apunta a la tabla de hijos"
    struct.pack_into("<I", out, lit, (arr_va - (LIT_ADD + 4)) & 0xFFFFFFFF)
    assert struct.unpack_from("<H", data, MOVS_N)[0] == 0x2200 | TABLA_N, "cuenta de hijos inesperada"
    struct.pack_into("<H", out, MOVS_N, 0x2200 | (TABLA_N + n))

    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    new_ph[-1][4] = new_ph[-1][5] = len(seg) + 32 * len(new_ph)
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


def delta_respecto_memoryrecall(caution_orig: bytes, delta_aelw: int) -> int:
    """Convierte la distancia a `RootAelWShutter` (la que devuelve `build_pp_menu.patch_caution`) en distancia a `RootMemoryRecallFn` (la que usa `patch_vu4`)."""
    import build_pp_gamma_menu as G
    segs = A._segments(caution_orig)
    _, dyn = A._dynamic(caution_orig, segs)
    va = lambda n: G.sym(caution_orig, segs, dyn, n)[2][0]
    return delta_aelw + va("cmnViewSettingNodeRootAelWShutter") - va(REF.decode())
