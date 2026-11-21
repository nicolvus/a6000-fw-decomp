"""G86-B — «LUT» elegible en las 12 ranuras del menú Fn (cierra G12-A2 y FN-LUT-4; ver docs/gui/g86-menu-fn-lut.md §4).

Hechos VERIFICADOS en los bytes del 3.21:
  * La lista de opciones de cada ranura (`CustomFunctionN`) la elige `CmnViewSettingNodeCustomFunctionN` por el tipo de modelo (`tbb` de 30 casos, p. ej. `CautionConfig+0x10650c`):
    el A6000 (tipo 29) usa `cmnViewSettingNodesCustomFunctionNType08` (26 nodos, NotSet al final) con su cuenta en `…NumOfCustomFunctionNType08` (dato). Matriz y cuenta llegan por el GOT.
  * El valor que guarda cada opción NO es su `0xf`: es `tabla[0xf]` con una tabla `u32[37]` por ranura en el gestor de procesos (la UI usa la copia de `viewUnified2.so`, G28).
    Los ids `0xf` de la ranura 1 van 0…36 (ShootMode = 36, NotSet = 35) y los de las ranuras 2…12 están desplazados +1 (ShootMode = 0, NotSet = 36): las 11 tablas de esas ranuras empiezan
    por el valor de ShootMode (`0x11`) y la de la ranura 1 lo lleva al final. Comprobado por nombre en las 36 opciones frente al `tbh` de `viewUnified4.so` (tests/test_g87_fn_asignacion.py).
Cambios: (1) matriz de 27 punteros en un segmento nuevo (25 originales con su ABS32, el nodo LUT nuevo, NotSet), GLOB_DAT de la matriz → RELATIVE al segmento, cuenta 26→27;
(2) opción LUT con el id de ShootMode de cada ranura (36 en la 1, 0 en las demás; el A6000 no ofrece ShootMode) y, en las 12 tablas de `viewUnified2.so`, la entrada de ShootMode pasa de `0x11`
a `0x26` (el valor que el despachador de `viewUnified4.so` lleva al hijo 39). Sin tocar código.
shortcut: ShootMode queda sin valor propio; solo existe en listas de otros modelos, no en el A6000. Para devolverlo: ampliar la tabla (código del gestor de procesos).
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import build_pp_gamma_menu as G

RES = 0x0204_0000
RANURAS = range(1, 13)
N_ORIG, POS_NOTSET = 26, 25
ID_SHOOTMODE = {1: 0x24, **{n: 0 for n in range(2, 13)}}   # 0xf/0x10 del nodo LUT por ranura (= id de ShootMode en esa ranura)
VALOR_LUT = 0x26                    # = fn_lut_menu.VALOR_LUT
TABLA_1 = [1, 2, 0xA, 5, 6, 0xC, 3, 4, 7, 8, 9, 0x12, 0xB, 0xF, 0xD, 0x10, 0xE, 0x13, 0x16, 0x15, 0x14, 0x17, 0x18, 0x19, 0x2A, 0x2B, 0x2D, 0x2F, 0x20, 0x21, 0x22, 0x2C, 0x2E, 0x25, 0x29, 0, 0x11]   # ranura 1
TABLA_N = [TABLA_1[-1], *TABLA_1[:-1]]                                                                                                                 # ranuras 2…12
AYUDA = "Selects the colour look (3D LUT) applied to photos and video."


def _pack(t) -> bytes:
    return b"".join(struct.pack("<I", x) for x in t)


def patch_vu2(data: bytes) -> bytes:
    """Valor de ShootMode (`0x11`) → `0x26` en las 12 tablas: 11 con él al principio y 1 (ranura 1) al final; no se aplica dos veces."""
    n_ant, n_1 = _pack(TABLA_N), _pack(TABLA_1)
    nue_n, nue_1 = _pack([VALOR_LUT, *TABLA_N[1:]]), _pack([*TABLA_1[:-1], VALOR_LUT])
    cuentas = (data.count(n_ant), data.count(n_1), data.count(nue_n), data.count(nue_1))
    if cuentas != (11, 1, 0, 0):
        raise ValueError(f"tablas opción→valor (ranuras 2…12, ranura 1, parcheadas): {cuentas}; se esperan (11, 1, 0, 0)")
    return data.replace(n_ant, nue_n).replace(n_1, nue_1)


def patch_caution(data: bytes, texto: int, ayuda: int) -> bytes:
    """`texto`/`ayuda`: ids de recurso (`0x0204xxxx & 0xffff`) de «LUT» y de su ayuda."""
    segs = A._segments(data)
    doff, dyn = A._dynamic(data, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = bytearray(data[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz])
    por_off = {struct.unpack_from("<I", rel, i)[0]: i for i in range(0, rel_sz, 8)}
    vt = G.sym(data, segs, dyn, "_ZTV18CmnViewSettingNode")[2][0] + 8
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(data) + A.ALIGN - 1) // A.ALIGN * A.ALIGN

    def construye(base):
        """Segmento con los 12 nodos LUT y las 12 matrices nuevas; devuelve (segmento, [(ranura, VA matriz)], [(VA, info de relocación)])."""
        seg, out, rels = G.Segmento(base), [], []
        for n in RANURAS:
            tri = [(0, 0, RES | texto), (6, 0, RES | ayuda), (0xB, 1, 0), (0xC, 1, 2), (0xF, 1, ID_SHOOTMODE[n]), (0x10, 1, ID_SHOOTMODE[n])]
            lista = seg.alloc([x for t in tri for x in t])
            kids = seg.alloc([0])
            props = seg.alloc([lista, len(tri)], {0: "R"})
            nodo = seg.alloc([vt, kids, 0, props] + [0] * 6, {0: "R", 1: "R", 3: "R"})
            _, _, (arr, size, _) = G.sym(data, segs, dyn, f"cmnViewSettingNodesCustomFunction{n}Type08")
            assert size == 4 * N_ORIG, (n, size)
            infos = [struct.unpack_from("<II", rel, por_off[arr + 4 * k])[1] for k in range(N_ORIG)]
            assert all(i & 0xFF == A.R_ARM_ABS32 for i in infos), n
            nueva = seg.alloc([nodo if k == POS_NOTSET else 0 for k in range(N_ORIG + 1)])
            rels += [(nueva + 4 * k, 23 if k == POS_NOTSET else infos[k if k < POS_NOTSET else k - 1]) for k in range(N_ORIG + 1)]
            out.append((n, nueva))
        return seg, out, rels + [(va, 23) for va, _ in seg.rels]

    n_rel = len(construye(new_va)[2])                                         # el nº de relocaciones no depende de la base
    seg, listas, rels = construye(new_va + (rel_sz + 8 * n_rel + 15) // 16 * 16)
    out = bytearray(data)
    rel_new = bytearray(rel)
    for n, nueva in listas:
        # GOT: GLOB_DAT contra el símbolo de la matriz → RELATIVE a la matriz nueva
        idx = G.sym(data, segs, dyn, f"cmnViewSettingNodesCustomFunction{n}Type08")[0]
        got = [(o, p) for p in range(0, rel_sz, 8) for o, i in [struct.unpack_from("<II", rel, p)] if i == (idx << 8 | 21)]
        assert len(got) == 1, (n, got)
        struct.pack_into("<II", rel_new, got[0][1], got[0][0], 23)
        struct.pack_into("<I", out, A._off(segs, got[0][0]), nueva)
        _, _, (cnt, csz, _) = G.sym(data, segs, dyn, f"cmnViewSettingNodesNumOfCustomFunction{n}Type08")
        assert csz == 4 and struct.unpack_from("<I", data, A._off(segs, cnt))[0] == N_ORIG
        struct.pack_into("<I", out, A._off(segs, cnt), N_ORIG + 1)
    for va, r in rels:
        rel_new += struct.pack("<II", va, r)
    assert len(rel_new) == rel_sz + 8 * n_rel
    blob = b"".join(struct.pack("<I", w) for w in seg.words)
    body = bytes(rel_new).ljust(seg.va - new_va, b"\0") + blob
    phdr_off = new_off + len(body)
    new_ph = [list(x) for x in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    new_ph[-1][4] = new_ph[-1][5] = len(body) + 32 * len(new_ph)
    body += b"".join(struct.pack("<8I", *x) for x in new_ph)
    res = bytearray(bytes(out).ljust(new_off, b"\0") + body)
    struct.pack_into("<I", res, 28, phdr_off)
    struct.pack_into("<H", res, 44, len(new_ph))
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", res, doff + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", res, doff + 8 * i + 4, len(rel_new))
    return bytes(res)
