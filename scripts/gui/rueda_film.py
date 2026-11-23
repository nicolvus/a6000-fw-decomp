"""G101 — «Film» asignable a la rueda de control: al girarla, la franja horizontal nativa (`PAS_MenuSelectBeltWheel`) recorre Off + los 38 looks.

Hechos VERIFICADOS en los bytes del 3.21 (docs/gui/g101-film-tecla-rueda.md):
  * Asignación: pid `0xdc` de `viewUnified2.so` (descriptor `0x4b76ac`, 5 opciones en `+0x15`, modelo `+0x20` = {Backup `0x1070c74`, tabla opción→valor}),
    tabla `[8, 0xb, 0xd, 0xe, 0]` = ISO, Balance, Estilo creativo, Efecto, No definido; lista de nodos `cmnViewSettingNodesRearWheelDefault` (5) de CautionConfig.
  * Las vistas que abren la franja eligen el nodo por ese valor con el mismo código: `ldrb r3,…; subs r3,#8; cmp r3,#6; bhi defecto; tbb …` y guardan el nodo con
    `str.w r3,[obj,#…]` 0x26 bytes después del `subs` (ViewStlrec `0x13f626` y ViewMovieRecPatch `0x3621be` de viewUnified2; ViewTriDial `0x21024` de viewUnified7).
    El valor 9 cae en «sin nodo».
Cambios:
  (1) CautionConfig: lista de la rueda con un nodo «Film» (`0xf` = 5) antes de «No definido».
  (2) viewUnified2: pid `0xdc` con 6 opciones, tabla `[…, 9]` y precauciones nuevas.
  (3) En cada vista, `subs r3,#8; cmp r3,#6` → `bl cueva`. La cueva: con 9 devuelve el nodo «Film» (palabra con `R_ARM_ABS32` contra un nodo raíz importado + distancia)
      y vuelve al `str.w` (lr + 0x22); con otro valor hace las dos instrucciones originales y `bx lr` (las banderas llegan intactas al `bhi`). Las tres funciones guardan lr.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import build_pp_gamma_menu as G

RES = 0x0204_0000
VALOR_FILM = 9
BK_RUEDA = 0x1070C74
DESC_RUEDA = 0x4B76AC                       # viewUnified2: descriptor del pid 0xdc
TABLA_RUEDA = (8, 0xB, 0xD, 0xE, 0)
LISTA, CUENTA = "cmnViewSettingNodesRearWheelDefault", "cmnViewSettingNodesNumOfRearWheelDefault"
POS_NOTSET = 4
SITIOS_VU2 = (0x13F626, 0x3621BE)           # ViewStlrec, ViewMovieRecPatch
SITIO_VU7 = 0x21024                         # ViewTriDial (evento 5)
A_STORE = 0x26                              # del `subs r3,#8` al `str.w r3,[obj,#…]`
SIMBOLO = "cmnViewSettingNodeRootISOSensitivity"   # importado de CautionConfig por vu2 y vu7: el nodo «Film» = SIMBOLO + distancia
ORIG = bytes.fromhex("083b062b")            # subs r3,#8; cmp r3,#6
TBB_DEFECTO = 1                             # índice valor−8 del 9 en el `tbb`
VALORES = (9, 10, 12)                       # valores libres del `tbb` (8…14): 9 = «Film», 10 = «Picture Profile» (G102), 12 libre


def _asm(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    return bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)[0])


def got_de(img: bytes) -> int:
    segs = A._segments(img)
    return {t: v for t, v in A._dynamic(img, segs)[1] if t}[3]          # DT_PLTGOT: base de los desplazamientos `ldr r3,[rGOT,r3]`


def _anade(data: bytes, palabras_de, codigo_de=None, parches=None) -> bytes:
    """Añade un segmento RW (tabla de relocaciones reubicada + `palabras`) y, si hay `codigo_de`, uno R+X; reubica la tabla de cabeceras al final.
    `palabras_de(va_palabras)` → (palabras, [(índice, info de relocación)]); `codigo_de(va_palabras, va_codigo)` → bytes; `parches(out, va_palabras, va_codigo, rel)`
    modifica el fichero y devuelve las relocaciones existentes a cambiar {offset en la tabla: (va, info)}."""
    segs = A._segments(data)
    doff, dyn = A._dynamic(data, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = bytearray(data[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz])
    al = lambda x: (x + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    rw_va, rw_off = al(top), al(len(data))
    n_rel = len(palabras_de(0)[1])
    pal_va = rw_va + (rel_sz + 8 * n_rel + 15) // 16 * 16
    palabras, rels = palabras_de(pal_va)
    rx_va = al(pal_va + 4 * len(palabras))
    rx_off = rw_off + (rx_va - rw_va)
    out = bytearray(data)
    for off, (va, info) in (parches(out, pal_va, rx_va, rel) if parches else {}).items():
        struct.pack_into("<II", rel, off, va, info)
    rel += b"".join(struct.pack("<II", pal_va + 4 * k, info) for k, info in rels)
    rw = bytes(rel).ljust(pal_va - rw_va, b"\0") + b"".join(struct.pack("<I", w & 0xFFFFFFFF) for w in palabras)
    codigo = codigo_de(pal_va, rx_va) if codigo_de else b""
    codigo += b"\0" * (-len(codigo) % 16)
    rw += b"\0" * (-len(rw) % 16)
    ph = [list(x) for x in segs] + [[1, rw_off, rw_va, rw_va, len(rw), len(rw), 6, A.ALIGN]]
    if codigo_de:                                        # la tabla de cabeceras va al final del segmento R+X
        ph.append([1, rx_off, rx_va, rx_va, 0, 0, 5, A.ALIGN])
        cola_off, cola = rx_off, codigo
    else:                                                # … o del RW
        cola_off, cola, rw = rw_off, rw, b""
    phdr_off = cola_off + len(cola)
    ph[-1][4] = ph[-1][5] = len(cola) + 32 * len(ph)
    res = bytearray(bytes(out).ljust(rw_off, b"\0") + rw)
    res = res.ljust(cola_off, b"\0") + cola + b"".join(struct.pack("<8I", *x) for x in ph)
    struct.pack_into("<I", res, 28, phdr_off)
    struct.pack_into("<H", res, 44, len(ph))
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", res, doff + 8 * i + 4, rw_va)
        if t == 0x12:
            struct.pack_into("<I", res, doff + 8 * i + 4, len(rel))
    return bytes(res)


def _rel_de(data: bytes, rel: bytearray, va: int) -> tuple[int, int]:
    """(offset en la tabla, info) de la relocación de la palabra `va`."""
    for p in range(0, len(rel), 8):
        o, info = struct.unpack_from("<II", rel, p)
        if o == va:
            return p, info
    raise ValueError(f"sin relocación en {va:#x}")


def patch_vistas(data: bytes, sitios, deltas) -> bytes:
    """Cueva común + `bl cueva` en cada sitio. `deltas` = {valor: VA del nodo en CautionConfig − VA de `SIMBOLO`} (un entero = solo el 9, «Film»)."""
    deltas = {VALOR_FILM: deltas} if isinstance(deltas, int) else dict(deltas)
    assert deltas and set(deltas) <= set(VALORES), deltas
    segs = A._segments(data)
    _, dyn = A._dynamic(data, segs)
    for s in sitios:
        o = A._off(segs, s)
        if data[o:o + 4] != ORIG:
            raise ValueError(f"{s:#x}: no es `subs r3,#8; cmp r3,#6` (¿ya parcheado?)")
        tbb = data[o + 10:o + 17]                        # tabla tras `tbb [pc, r3]` (o + 6)
        assert data[o + 6:o + 8] == b"\xdf\xe8", hex(s)
        assert all(o + 10 + 2 * tbb[v - 8] == o + A_STORE - 2 for v in deltas), (hex(s), tbb.hex())   # los valores nuevos iban al `movs r3,#0` (defecto)
        assert data[o + A_STORE + 1] in (0xF8,) and data[o + A_STORE] in (0xC4, 0xC5), hex(s)                     # str.w r3,[r4|r5,#…]
    idx = G.sym(data, segs, dyn, SIMBOLO)[0]
    vals = sorted(deltas)
    n = len(vals)

    def codigo(pal_va, rx_va):
        # n × (cmp r3,#v; beq eK) · subs r3,#8; cmp r3,#6; bx lr · n × (eK: ldr r3,[pc,#…]; add r3,pc; b carga) · carga: ldr r3,[r3]; add.w lr,…; bx lr · literales
        e0 = rx_va + 4 * n + 6
        carga = e0 + 6 * n
        lit0 = (carga + 8 + 3) & ~3
        c = b"".join(_asm(f"cmp r3, #{v}; beq {e0 + 6 * k:#x}", rx_va + 4 * k) for k, v in enumerate(vals))
        c += _asm("subs r3, #8; cmp r3, #6; bx lr", rx_va + 4 * n)
        lits = []
        for k in range(n):
            a = e0 + 6 * k
            c += struct.pack("<H", 0x4B00 | (lit0 + 4 * k - ((a + 4) & ~3)) // 4) + _asm(f"add r3, pc; b {carga:#x}", a + 2)   # ldr r3,[pc,#imm]
            lits.append((pal_va + 4 * k - (a + 2 + 4)) & 0xFFFFFFFF)
        c += _asm(f"ldr r3, [r3]; add.w lr, lr, #{A_STORE - 4}; bx lr", carga)
        assert len(c) == carga + 8 - rx_va, len(c)
        return c.ljust(lit0 - rx_va, b"\0") + b"".join(struct.pack("<I", x) for x in lits)

    def parches(out, pal_va, rx_va, rel):
        for s in sitios:
            out[A._off(segs, s):A._off(segs, s) + 4] = _asm(f"bl {rx_va:#x}", s)
        return {}

    return _anade(data, lambda va: ([deltas[v] for v in vals], [(k, idx << 8 | 2) for k in range(n)]), codigo, parches)


def patch_descriptor(data: bytes, valores=(VALOR_FILM,)) -> bytes:
    """pid 0xdc: 5 + len(valores) opciones, tabla opción→valor `[8, 0xb, 0xd, 0xe, 0, *valores]` y precauciones nuevas en un segmento RW."""
    segs = A._segments(data)
    w = lambda va, n=1: struct.unpack_from(f"<{n}I", data, A._off(segs, va))
    o = A._off(segs, DESC_RUEDA)
    modelo = w(DESC_RUEDA + 0x20)[0]
    bk, tabla = w(modelo, 2)
    if data[o + 0x15] != len(TABLA_RUEDA) or bk != BK_RUEDA or w(tabla, 5) != TABLA_RUEDA:
        raise ValueError("el descriptor de la rueda no es el del 3.21 (¿ya parcheado?)")
    caut = w(DESC_RUEDA + 4)[0]
    precs = list(w(caut, 5))
    n = len(TABLA_RUEDA) + len(valores)

    def parches(out, pal_va, rx_va, rel):
        out[o + 0x15] = n
        cambios = {}
        for va, nuevo in ((modelo + 4, pal_va), (DESC_RUEDA + 4, pal_va + 4 * n)):
            p, info = _rel_de(data, rel, va)
            assert info == 23, (hex(va), info)
            struct.pack_into("<I", out, A._off(segs, va), nuevo)
            cambios[p] = (va, 23)
        return cambios

    return _anade(data, lambda va: ([*TABLA_RUEDA, *valores, *precs, *[precs[-1]] * len(valores)], []), None, parches)


def patch_caution(data: bytes, texto, ayuda=None) -> bytes:
    """Lista de la rueda 5 → 5 + n nodos: los nuevos (`0xf = 0x10 = 5 + k`, el orden de `valores` en `patch_descriptor`) antes de «No definido»;
    GLOB_DAT de la matriz → RELATIVE a la nueva. `texto` = [(id texto, id ayuda), …] o, compatibilidad, `texto, ayuda` de «Film»."""
    nodos = [(texto, ayuda)] if ayuda is not None else list(texto)
    segs = A._segments(data)
    _, dyn = A._dynamic(data, segs)
    tg = {t: v for t, v in dyn if t}
    tabla = data[A._off(segs, tg[0x11]):A._off(segs, tg[0x11]) + tg[0x12]]
    por = {struct.unpack_from("<I", tabla, i)[0]: struct.unpack_from("<I", tabla, i + 4)[0] for i in range(0, len(tabla), 8)}
    vt = G.sym(data, segs, dyn, "_ZTV18CmnViewSettingNode")[2][0] + 8
    idx_l, _, (arr, size, _) = G.sym(data, segs, dyn, LISTA)
    _, _, (cnt, _, _) = G.sym(data, segs, dyn, CUENTA)
    if struct.unpack_from("<I", data, A._off(segs, cnt))[0] != 5 or size != 20:
        raise ValueError("la lista de la rueda no es la del 3.21 (¿ya parcheada?)")
    orig = [(struct.unpack_from("<I", data, A._off(segs, arr + 4 * k))[0], por[arr + 4 * k]) for k in range(5)]
    assert all(i & 0xFF == A.R_ARM_ABS32 for _, i in orig)
    n = len(nodos)
    TAM = 18 + 1 + 2 + 10                                         # por nodo: 6 tripletas, hijos (0), props {lista, 6}, nodo de 10 palabras
    MAT = TAM * n                                                 # matriz al final

    def palabras(base):
        va = lambda k: base + 4 * k
        ws, rels, ptr = [], [], []
        for k, (t, a) in enumerate(nodos):
            b = TAM * k
            tri = [(0, 0, RES | t), (6, 0, RES | a), (0xB, 1, 0), (0xC, 1, 2), (0xF, 1, 5 + k), (0x10, 1, 5 + k)]
            ws += [x for tr in tri for x in tr] + [0] + [va(b), len(tri)] + [vt, va(b + 18), 0, va(b + 19)] + [0] * 6
            rels += [(b + 19, 23), (b + 21, 23), (b + 22, 23), (b + 24, 23)]
            ptr.append(va(b + 21))
        ws += [w for w, _ in orig[:POS_NOTSET]] + ptr + [orig[POS_NOTSET][0]]
        rels += [(MAT + k, orig[k][1]) for k in range(POS_NOTSET)] + [(MAT + POS_NOTSET + k, 23) for k in range(n)] + [(MAT + POS_NOTSET + n, orig[POS_NOTSET][1])]
        return ws, rels

    def parches(out, pal_va, rx_va, rel):
        got = [(p, o) for p in range(0, len(rel), 8) for o, i in [struct.unpack_from("<II", rel, p)] if i == (idx_l << 8 | 21)]
        assert len(got) == 1, got
        p, o = got[0]
        struct.pack_into("<I", out, A._off(segs, o), pal_va + 4 * MAT)
        struct.pack_into("<I", out, A._off(segs, cnt), 5 + n)
        return {p: (o, 23)}

    return _anade(data, palabras, None, parches)
