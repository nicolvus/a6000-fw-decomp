#!/usr/bin/env python3
"""G104 §8.5/§8.6 — Pantalla ISO hasta 409600 (fw3.21+).

`patch` (§8.5, 3 B): la vista `ViewIsoSensitivity` de `viewUnified4.so` oculta a mano las filas 32000 (id `0x1f`), 40000 (`0x20`) y 51200 (`0x21`),
que ya existen en su tabla de menú (`CmnViewMenuItemStruct`, `0x1b113c`): `0xf0ae0` las marca válidas y luego llama a
`CmnMenuTableUtil::setValid(id, false)`; el parche cambia `movs r2,#0` → `#1` en esas tres llamadas. `libObj`, `getIso` y `processDataMgr` ya llegan a 51200.

`patch_filas` + `patch_vu2` (§8.6): filas 64000…409600 (`VALORES`), como la A7S 3.20:
  * vu4: tabla de menú copiada a un segmento nuevo con 9 ítems más (filas `0x40…0x48`; `0x3f` es el centinela «sin fila» de `0xef894`),
    fila → enum (`0xef90c`, defecto `0xef996`) y enum → fila (`0xef894`, defecto `0xef8a8`) con cuevas para los enums nuevos `0x50…0x58`
    (`0x4f` sigue siendo ISO_INVALID).
  * vu2 (`WrapperIso`): `getIso` código de modelo → enum (`0x1c14d8`), `setIso` enum → código (`0x1c1dda`, mismo objeto que los casos
    originales y la cola `0x1c27d2`) y `isInhOn` enum → id de proceso (`0x1c1a20`, defecto `0x1c1bf6`): los nuevos usan el id `0x20`,
    el de 51200 (G108: el `0x2f` anterior es el del enum nativo `0x10`; con un ISO 128000+ guardado la app no arrancaba).
Códigos de modelo (`getModelInfo("@M00B")`): 64000/80000/102400 = `0x27…0x29` (ya en `libObj`), 128000…409600 = `0x4b…0x50` (los de la A7S; `libObj`
del A6000 aún no los acepta, ISO-409-A).
Uso: iso_ui_patch.py ENTRADA.so SALIDA.so   (solo los 3 B de §8.5; valida los bytes originales; idempotente)
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import rueda_film as R

# (dirección del `movs r2,#0`, id de fila que va justo antes en `movs r1,#id`)
SITIOS = ((0xF0B26, 0x21), (0xF0B32, 0x20), (0xF0B3E, 0x1F))

VALORES = (64000, 80000, 102400, 128000, 160000, 204800, 256000, 320000, 409600)
CODIGOS = (0x27, 0x28, 0x29, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50)
ENUM0, FILA0, PID_NUEVO = 0x50, 0x40, 0x20   # G108: pid de proceso de 51200 (enum 0x4e), no el 0x2f del enum 0x10 (bloqueaba el arranque)
# filas que lleva el CFW: hasta 204800. 256000…409600 se eligen y llegan a `libObj`, pero `libObj` devuelve el código 0x4d (G104 §8.7)
N_CFW = 6
MENU_CAB, MENU_TABLA, MENU_N = 0x1B113C, 0x1B1164, 0x22
GUIA_51200, FLAGS_FILA = 0x0204E686, 0x200            # +0x14 y +0x1c de la fila 51200 (y de las de la A7S)
# viewUnified4: defectos de fila→enum y enum→fila (`movs r0,#0x4f|#0x3f; pop {r7,pc}`)
VU4_FILA_ENUM, VU4_ENUM_FILA = 0xEF996, 0xEF8A8
# `0xf0ae0` marca válidas las filas con ids 0…getCountAll−1 (`mov r6, r0`): con las filas nuevas (ids 0x40…) el recuento se queda corto
# (medido en el arnés: 256000…409600 no aparecían) → límite fijo `movs r6, #FILA0 + n`
VU4_VALIDAS = 0xF0B02
# viewUnified2 (WrapperIso)
GET_CMP, GET_ERR = 0x1C14D8, 0x1C19B6                 # cmp r0,#0x26; bne.w err; movs r3,#0x4e; str r3,[r6]
SET_CMP, SET_ERR, SET_COLA = 0x1C1DDA, 0x1C28F0, 0x1C27D2   # cmp r3,#0x4c; bhi.w err; tbh …
SET_NEW, SET_CTOR = 0xE6FBC, 0xEE040                  # operator new (PLT) y el constructor del valor (casos originales)
INH_DEF = 0x1C1BF6                                     # movs r0,#0; pop {r7,pc}
# indicador ISO de la pantalla de disparo (vu2 `0x2d7940`, código de `getModelInfo` 0x1f4): solo pinta el número si código ≤ 0x26 (tabla `0x3ceeec`,
# ISO por código hasta 0x29); `r4` = juego de iconos (1 = MFNR, código > 0x39)
IND_RANGO, IND_SIGUE, IND_NUMERO = 0x2D7A2C, 0x2D7A42, 0x2D7B44   # cmp r3,#0x26; bgt IND_SIGUE
IND_TABLA, IND_TABLA_ISO = 0x2D7B62, 0x3CEEEC                     # ldr r2,[pc]; add r2,pc; ldr.w r2,[r2,r3,lsl #2]


def patch(d: bytes) -> bytes:
    out = bytearray(d)
    for a, fila in SITIOS:
        assert out[a - 2:a] == bytes((fila, 0x21)), f"movs r1,#{fila:#x} no está en {a - 2:#x}"
        assert out[a + 1] == 0x22 and out[a] in (0, 1), f"bytes inesperados en {a:#x}: {out[a:a + 2].hex()}"
        out[a] = 1
    return bytes(out)


def _espera(d: bytes, segs, va: int, hexa: str) -> None:
    o = A._off(segs, va)
    if d[o:o + len(hexa) // 2] != bytes.fromhex(hexa):
        raise ValueError(f"{va:#x}: bytes {d[o:o + len(hexa) // 2].hex()} ≠ {hexa} (¿otra versión o ya parcheado?)")


def patch_filas(d: bytes, textos: dict, iconos: dict, n: int = len(VALORES)) -> bytes:
    """vu4: `patch` + las `n` primeras filas nuevas de `VALORES`. `textos[valor]` = id de texto (16 bits); `iconos[valor]` = (icono de la lista, icono seleccionado) (16 bits)."""
    d = patch(d)
    segs = A._segments(d)
    _, dyn = A._dynamic(d, segs)
    tg = {t: v for t, v in dyn if t}
    rel = d[A._off(segs, tg[0x11]):A._off(segs, tg[0x11]) + tg[0x12]]
    por = {struct.unpack_from("<I", rel, i)[0]: struct.unpack_from("<I", rel, i + 4)[0] for i in range(0, len(rel), 8)}
    cab = A._off(segs, MENU_CAB)
    if struct.unpack_from("<2I", d, cab) != (MENU_TABLA, MENU_N) or por.get(MENU_CAB) != 23:
        raise ValueError("la cabecera de la tabla ISO no es la del 3.21 (¿ya parcheado?)")
    _espera(d, segs, VU4_FILA_ENUM, "4f2080bd")
    _espera(d, segs, VU4_ENUM_FILA, "3f2080bd")
    _espera(d, segs, VU4_VALIDAS, "0646")
    viejas = list(struct.unpack_from(f"<{10 * MENU_N}I", d, A._off(segs, MENU_TABLA)))
    rels = [(k, por[MENU_TABLA + 4 * k]) for k in range(10 * MENU_N) if MENU_TABLA + 4 * k in por]
    nuevas = []
    for k, v in enumerate(VALORES[:n]):
        nuevas += [0, 0, FILA0 + k, 0x02040000 | textos[v], 0x02050000 | iconos[v][0], GUIA_51200, 0x02050000 | iconos[v][1], FLAGS_FILA, 0, 0]

    def codigo(_, rx):
        return R._asm(f"sub.w r0, r1, #{FILA0}; cmp r0, #{n - 1}; ite ls; addls r0, r0, #{ENUM0}; movhi r0, #0x4f; pop {{r7, pc}}", rx).ljust(16, b"\0") \
            + R._asm(f"sub.w r0, r1, #{ENUM0 - 1}; cmp r0, #{n - 1}; ite ls; addls r0, r0, #{FILA0}; movhi r0, #0x3f; pop {{r7, pc}}", rx + 16)

    def parches(out, pal, rx, _):
        struct.pack_into("<2I", out, cab, pal, MENU_N + n)        # la palabra 0 conserva su RELATIVE: el valor guardado es el sumando
        out[A._off(segs, VU4_FILA_ENUM):A._off(segs, VU4_FILA_ENUM) + 4] = R._asm(f"b.w {rx:#x}", VU4_FILA_ENUM)
        out[A._off(segs, VU4_ENUM_FILA):A._off(segs, VU4_ENUM_FILA) + 4] = R._asm(f"b.w {rx + 16:#x}", VU4_ENUM_FILA)
        out[A._off(segs, VU4_VALIDAS):A._off(segs, VU4_VALIDAS) + 2] = R._asm(f"movs r6, #{FILA0 + n}", VU4_VALIDAS)
        return {}

    assert len(codigo(0, 0x400000)) == 30
    return R._anade(d, lambda _: (viejas + nuevas, rels), codigo, parches)


def patch_vu2(d: bytes, n: int = len(VALORES)) -> bytes:
    """vu2 (`WrapperIso`): enums `0x50…0x58` ↔ códigos `CODIGOS` en `getIso`/`setIso`, e id de proceso `PID_NUEVO` en `isInhOn`."""
    segs = A._segments(d)
    _espera(d, segs, GET_CMP, "262840f06c824e233360")
    _espera(d, segs, SET_CMP, "4c2b00f28885")
    _espera(d, segs, INH_DEF, "002080bd")
    _espera(d, segs, IND_RANGO, "262b08dc")
    _espera(d, segs, IND_TABLA, "3d4a7a4452f82320")
    par = list(enumerate(CODIGOS[:n]))
    get = "movs r3, #0x4e; cmp r0, #0x26; beq g_ok; " + "".join(f"movs r3, #{ENUM0 + k}; cmp r0, #{c}; beq g_ok; " for k, c in par) \
        + f"b.w {GET_ERR:#x}; g_ok: bx lr"
    set_ = (f"cmp r3, #0x4c; bls s_ok; ldr r2, [r7, #4]; sub.w r2, r2, #{ENUM0}; cmp r2, #{len(par) - 1}; bls s_new; b.w {SET_ERR:#x}; "
            f"s_new: movs r0, #0x10; movs r4, #0; blx {SET_NEW:#x}; ldr r2, [r7, #4]; "   # r0-r3 caen en la llamada: se relee el enum
            + "".join(f"movs r1, #{c}; cmp r2, #{ENUM0 + k}; beq s_ctor; " for k, c in par)
            + f"s_ctor: mov r5, r4; mov r6, r0; bl {SET_CTOR:#x}; b.w {SET_COLA:#x}; s_ok: bx lr")
    inh = f"sub.w r3, r1, #{ENUM0 - 1}; cmp r3, #{len(par) - 1}; bhi i_no; movs r3, #{PID_NUEVO}; str r3, [r2]; movs r0, #1; pop {{r7, pc}}; i_no: movs r0, #0; pop {{r7, pc}}"
    # indicador de la pantalla de disparo: los códigos nuevos van a la rama del número con el juego de iconos normal (r4 = 0)
    altos = [(c, v) for c, v in zip(CODIGOS[:n], VALORES) if c > 0x29]
    assert altos, "n ≥ 4 (al menos 128000)"
    c0 = altos[0][0]
    assert [c for c, _ in altos] == list(range(c0, c0 + len(altos)))
    rango = (f"cmp r3, #0x26; ble r_ok; cmp r3, #0x29; ble r_num; sub.w r2, r3, #{c0}; cmp r2, #{len(altos) - 1}; bls r_num; b.w {IND_SIGUE:#x}; "
             f"r_num: movs r4, #0; b.w {IND_NUMERO:#x}; r_ok: bx lr")

    def numero(va):
        """r2 = ISO del código r3: tabla original (≤ 0x29 y los de MFNR) o la propia, tras el código (40 B)."""
        t1, t2 = (IND_TABLA_ISO - (va + 20)) & 0xFFFFFFFF, 4
        c = R._asm(f"sub.w r2, r3, #{c0}; cmp r2, #{len(altos) - 1}; bls n_new; movw r2, #{t1 & 0xFFFF}; movt r2, #{t1 >> 16}; add r2, pc; "
                   f"ldr.w r2, [r2, r3, lsl #2]; bx lr; n_new: movw r3, #{t2}; movt r3, #0; add r3, pc; ldr.w r2, [r3, r2, lsl #2]; bx lr", va)
        assert len(c) == 40, len(c)
        return c + b"".join(struct.pack("<I", v) for _, v in altos)

    def cuevas(rx):
        va, c = [], b""
        for t in (get, set_, inh, rango, numero):
            va.append(rx + len(c))
            c += t(rx + len(c)) if callable(t) else R._asm(t, rx + len(c))
            c += b"\0" * (-len(c) % 4)
        return c, va

    def parches(out, _, rx, __):
        va = cuevas(rx)[1]
        for sitio, b in ((GET_CMP, R._asm(f"bl {va[0]:#x}", GET_CMP) + bytes.fromhex("00bf00bf")),
                         (SET_CMP, R._asm(f"bl {va[1]:#x}", SET_CMP) + bytes.fromhex("00bf")),
                         (INH_DEF, R._asm(f"b.w {va[2]:#x}", INH_DEF)),
                         (IND_RANGO, R._asm(f"bl {va[3]:#x}", IND_RANGO)),
                         (IND_TABLA, R._asm(f"bl {va[4]:#x}", IND_TABLA) + bytes.fromhex("00bf00bf"))):
            out[A._off(segs, sitio):A._off(segs, sitio) + len(b)] = b
        return {}

    return R._anade(d, lambda _: ([], []), lambda _, rx: cuevas(rx)[0], parches)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    Path(dst).write_bytes(patch(Path(src).read_bytes()))
    print("ok", dst)
