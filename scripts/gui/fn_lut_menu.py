#!/usr/bin/env python3
"""G86 — opción «LUT» en el menú Fn (lado `viewUnified4.so`): el nodo de ajuste «LUT» (el de la carpeta CFW, mismo pid/Backup) pasa a ser un hijo más de la raíz de
la franja Fn, con la vista nativa de opciones (título, fila ◄ ► con la actual resaltada, valor en la casilla).

Mecanismo (VERIFICADO en bytes del 3.21, ver docs/gui/g86-menu-fn-lut.md):
  * La vista `FNMENU` guarda por ranura `[this+0x258+8k]` = valor de Backup de la asignación y `[this+0x25c+8k]` = nº de serie (SRNum) del hijo de la raíz Fn
    (`CmnViewSettingNode` de 38 hijos, `0x1bb940`, hijos en `0x1b0d28`); el paso valor→SRNum es un `tbh` de 0x30 casos en `0xdd078`.
  * Se añade un hijo 39 (SRNum 39 = `0x27`) con el nodo «LUT» y el valor de asignación `0x26` (hasta ahora «por defecto», sin efecto) → SRNum `0x27`.
  * Sin hueco de código en alcance del `tbh`, 3 bloques contiguos de 8 B se recompactan a 4 B + un cuerpo común, lo que libera los 8 B del bloque nuevo.
Fuera de este módulo (G12-A2): la lista de asignación de cada ranura Fn (`CautionConfig.so`, 12 nodos × 37 opciones) debe ofrecer una opción con `0xf/0x10 = 0x26`.
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
BLOQUES = 0xDD0FE                              # 3 bloques de 8 B: valores 3, 1, 4 (SRNum 2, 1, 3)
VALOR_LUT, SRNUM_LUT = 0x26, 0x27
TABLA_VA, TABLA_N = 0x1B0D28, 38               # hijos de la raíz Fn
LIT_LDR, LIT_ADD, MOVS_N = 0xE0BA6, 0xE0BAE, 0xE0BAA   # `ldr r1,[pc,#0xbc]; … add r1,pc` del ctor y `movs r2,#0x26`
REF = b"cmnViewSettingNodeRootMemoryRecallFn"  # símbolo ya importado de CautionConfig; el hijo nuevo = REF + delta


def _asm(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def _bloques() -> tuple[bytes, bytes]:
    """(originales, nuevos) de los 24 B en `BLOQUES`. Nuevos: 3 × (`movs r3,#N; b.n común`) + el de LUT + cuerpo común (`add.w r4,r4,r5,lsl #3; b.n FIN`)."""
    orig = b"".join(_asm(f"add.w r4, r4, r5, lsl #3; movs r3, #{n}; b.n {FIN:#x}", BLOQUES + 8 * i) for i, n in enumerate((2, 1, 3)))
    comun = BLOQUES + 16
    nuevo = b"".join(_asm(f"movs r3, #{n}; b.n {comun:#x}", BLOQUES + 4 * i) for i, n in enumerate((2, 1, 3, SRNUM_LUT)))
    nuevo += _asm(f"add.w r4, r4, r5, lsl #3; b.n {FIN:#x}", comun) + b"\x00\xbf"     # + nop de relleno
    assert len(orig) == len(nuevo) == 24
    return orig, nuevo


def _entrada(valor: int, destino: int) -> tuple[int, int]:
    return TBH + 2 * valor, (destino - TBH) // 2


def patch_vu4(data: bytes, delta: int) -> bytes:
    """`delta` = VA del nodo «LUT» en CautionConfig − VA de `cmnViewSettingNodeRootMemoryRecallFn` (distancia fija dentro de esa biblioteca)."""
    out = bytearray(data)
    orig, nuevo = _bloques()
    if data[BLOQUES:BLOQUES + 24] != orig:
        raise ValueError("bloques del despachador distintos del 3.21")
    esperado = {1: BLOQUES + 8, 3: BLOQUES, 4: BLOQUES + 16, VALOR_LUT: None}
    for v, dst in esperado.items():
        a, _ = _entrada(v, 0)
        cur = TBH + 2 * struct.unpack_from("<H", data, a)[0]
        if dst is None:
            if cur != 0xDD23A:
                raise ValueError("el valor 0x26 ya tiene bloque")
        elif cur != dst:
            raise ValueError(f"tabla del valor {v:#x} inesperada")
    out[BLOQUES:BLOQUES + 24] = nuevo
    for v, dst in ((1, BLOQUES + 4), (4, BLOQUES + 8), (VALOR_LUT, BLOQUES + 12)):
        a, u = _entrada(v, dst)
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
    slots.append(delta & 0xFFFFFFFF)
    info.append((ref_sym << 8) | A.R_ARM_ABS32)

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
    struct.pack_into("<H", out, MOVS_N, 0x2200 | (TABLA_N + 1))

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
