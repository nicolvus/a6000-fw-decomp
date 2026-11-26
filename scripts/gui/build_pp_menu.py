#!/usr/bin/env python3
"""G23 — paquete de prueba del MENÚ COMPLETO de Picture Profile (A6300/A7S) para la A6000 fw3.21 (solo ficheros; no toca la cámara).

Todo son datos, sin código nuevo (G23 «Más páginas»): `pp_menu_spec.py` define los 26 ajustes (claves de la A7S, rangos del validador de la A6000) y el árbol
carpeta → páginas → ajustes/carpetas. Se construye:
  lib/viewUnified2.so             espacio de pids ampliado + descriptores de PP en pids nuevos dentro de la copia del gestor de procesos (pid_space.py, G28)
  lib/CautionConfig.so            nodos de datos puros (raíz+opciones de cada ajuste, carpetas y páginas) en un PT_LOAD RW con relocaciones RELATIVE
  lib/viewUnified2.so             entrada nueva = carpeta «Picture Profile» en las 5 páginas del menú (add_menu_entry.py)
  share/app/string_<idioma>.uxc   textos en ranuras libres (traducción de la A6300 si el inglés coincide; si no, el literal)
Uso: build_pp_menu.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [--saturacion-a6300] [--gamma-slog] [--color-gamut] [--copy-reset] [--hlg]
Las cuatro opciones parchean `libObj.so` (patch_libobj_pp.py). Sin `--copy-reset` el menú no lleva Copy ni Reset: la `libObj` original rechaza sus eventos 0x41/0x42.
"""
import hashlib
import json
import struct
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lut"))
import add_menu_entry as A
import build_pp_gamma_menu as G
import fn_lut_listas
import fn_lut_menu
import patch_libobj_pp
import pid_space
import pp_descriptors
import pp_factory
import pp_menu_spec as M
import pp_valuecheck_patch
import rueda_film
import silent_descriptor
import uxc_strings

RES = 0x0204_0000
RES_IMAGEN = 0x0205_0000


FN_TREES: list = []      # ajustes que solo se cuelgan del menú Fn (nodo suelto, sin entrada en las páginas del menú): sus VA relativas quedan en FN_DELTAS (fn_lut_menu.py)
FN_DELTAS: list = []
RUEDA: list = []         # G101/G102: nodos de FN_TREES también asignables a la rueda de control, con los valores `rueda_film.VALORES` en orden (9 «Film», 10 …)
FN_AYUDA: dict = {}      # G102: texto de ayuda de cada nodo de FN_TREES en la lista de asignación (por defecto el de «LUT»/«Film»)
SD_USERLAND = False      # G89: añade el userland de lectura de `.cube` de la SD a viewUnified2.so (lut_sd_vu2.py)
ICONOS: dict = {}        # G110/G111 §15: {ajuste: [id de imagen (16 bits) por opción]} → propiedad 1 de cada opción (70×60, como los ajustes nativos de icono simple)
EXTRA_TREES: list = []   # carpetas adicionales (p. ej. «CFW» de build_cfw_objetivos): sus ajustes ya están en M.SETTINGS/M.PIDS; cada una entra como entrada propia del menú


def textos(tree=M.TREE, settings=M.SETTINGS):
    out = []

    def add(t):
        if t not in out:
            out.append(t)

    def walk(n):
        if isinstance(n, str):
            s = settings[n]
            add(s.label)
            for t, _ in s.opciones:
                add(t)
        else:
            add(n[1])
            for pg in n[2]:
                for c in pg:
                    walk(c)

    walk(tree)
    for extra in (*EXTRA_TREES, *FN_TREES):
        walk(extra)
    for f in FN_TREES:
        add(FN_AYUDA.get(f, fn_lut_listas.AYUDA))
    return out


def build_nodes(seg, vt, ids, tree=M.TREE, settings=M.SETTINGS, pids=M.PIDS):
    """Crea los nodos en `seg` y devuelve la VA de la carpeta raíz. Cada nodo: {vtable, hijos, cuenta, props, 0×6}; props = {lista, nº tripletas}."""
    def nodo(tri, hijos):
        lst = seg.alloc([x for t in tri for x in t])
        kids = seg.alloc(hijos or [0], {i: "R" for i in range(len(hijos))})
        props = seg.alloc([lst, len(tri)], {0: "R"})
        return seg.alloc([vt, kids, len(hijos), props] + [0] * 6, {0: "R", 1: "R", 3: "R"})

    lt = lambda t: RES | ids[t]
    pid_de = {s: pids[i] for i, s in enumerate(settings)}

    def build(n):
        if isinstance(n, str):
            s = settings[n]
            ico = ICONOS.get(n)
            assert not ico or len(ico) == len(s.opciones), (n, len(ico), len(s.opciones))
            img = lambda k: [(1, 0, RES_IMAGEN | ico[k])] if ico else []      # la 4 es del patrón del Estilo creativo (icono arriba + valores debajo)
            ops = [nodo([(0, 0, lt(t)), *img(k), (6, 0, lt(t)), (0xB, 1, 0), (0xC, 1, 1), (0xF, 1, k), (0x10, 1, k)], []) for k, (t, _) in enumerate(s.opciones)]
            return nodo([(0, 0, lt(s.label)), (6, 0, lt(s.label)), (0xB, 1, 2), (0xC, 1, 0), (0xE, 1, pid_de[n])], ops)
        pages = [nodo([(0xB, 1, 0)], [build(c) for c in pg]) for pg in n[2]]
        return nodo([(0, 0, lt(n[1])), (6, 0, lt(n[1])), (0xB, 1, 0), (0xC, 1, 3)], pages)

    return build(tree)


def patch_caution(data: bytes, ids: dict):
    segs = A._segments(data)
    _, dyn = A._dynamic(data, segs)
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = data[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(data) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    vt = G.sym(data, segs, dyn, "_ZTV18CmnViewSettingNode")[2][0] + 8
    ref = G.sym(data, segs, dyn, "cmnViewSettingNodeRootAelWShutter")[2][0]

    def run(base):
        seg = G.Segmento(base)
        return seg, [build_nodes(seg, vt, ids, t, M.SETTINGS, M.PIDS) for t in (M.TREE, *EXTRA_TREES, *FN_TREES)]

    n_rel = len(run(new_va)[0].rels)                      # el nº de relocaciones no depende de la base
    seg, carpetas = run(new_va + (rel_sz + 8 * n_rel + 15) // 16 * 16)
    rel_new = bytearray(rel)
    for va, r in seg.rels:
        rel_new += struct.pack("<II", va, 0x17)
    assert len(rel_new) == rel_sz + 8 * n_rel
    blob = b"".join(struct.pack("<I", w) for w in seg.words)
    body = bytes(rel_new).ljust(seg.va - new_va, b"\0") + blob
    phdr_off = new_off + len(body)
    new_ph = [list(x) for x in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    new_ph[-1][4] = new_ph[-1][5] = len(body) + 32 * len(new_ph)
    body += b"".join(struct.pack("<8I", *x) for x in new_ph)
    res = bytearray(data.ljust(new_off, b"\0") + body)
    struct.pack_into("<I", res, 28, phdr_off)
    struct.pack_into("<H", res, 44, len(new_ph))
    doff, _ = A._dynamic(data, segs)
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", res, doff + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", res, doff + 8 * i + 4, len(rel_new))
    deltas = [c - ref for c in carpetas[:1 + len(EXTRA_TREES)]]
    FN_DELTAS[:] = [c - ref for c in carpetas[1 + len(EXTRA_TREES):]]
    return bytes(res), deltas[0] if len(deltas) == 1 else deltas


def _va(lib: bytes, nombre: str) -> int:
    segs = A._segments(lib)
    return G.sym(lib, segs, A._dynamic(lib, segs)[1], nombre)[2][0]


def main(dev_a, dev_b, dest, saturacion_a6300=False, gamma_slog=False, color_gamut=False, acciones=False, entradas_previas=(), silent=False, hlg=False):
    a, b, dest = Path(dev_a) / "nflasha15_unpacked_unpacked", Path(dev_b) / "nflasha15_unpacked_unpacked", Path(dest)
    (dest / "lib").mkdir(parents=True, exist_ok=True)
    (dest / "share/app").mkdir(parents=True, exist_ok=True)
    manifest = {"originales": {}, "parcheados": {}, "idiomas": []}

    def emit(rel, data):
        (dest / rel).write_bytes(data)
        manifest["originales"][rel] = hashlib.sha256((a / rel).read_bytes()).hexdigest()
        manifest["parcheados"][rel] = hashlib.sha256(data).hexdigest()

    txt = textos(M.TREE, M.SETTINGS)
    libres = G.free_ids(a, len(txt), {0xF3E8, 0xF515, 0xF56A})
    assert len(libres) == len(txt)
    ids = dict(zip(txt, libres))
    ajustes = [pp_descriptors.Ajuste(M.PIDS[i], s.clave, tuple(v for _, v in s.opciones), s.evento, s.id_get, s.clave_get, s.backup) for i, s in enumerate(M.SETTINGS.values())]
    if saturacion_a6300 or gamma_slog or color_gamut or acciones:     # opt-in: ver patch_libobj_pp.py
        lo = (a / "lib/libObj.so").read_bytes()
        lo = patch_libobj_pp.patch(lo) if saturacion_a6300 else lo
        lo = patch_libobj_pp.patch_gamma(lo, hlg=hlg) if gamma_slog or acciones else lo
        lo = patch_libobj_pp.patch_actions(lo) if acciones else lo
        lo = patch_libobj_pp.patch_color(lo) if color_gamut else lo                # G33-B §10: sin patch_bw, el núcleo trata B&W (pp_bw_mono_patch)
        # G107: el validador de órdenes (`EnumValueCheck`) debe admitir los Color Mode/Gamma nuevos o la orden no sale (PP7–PP10, S-Gamut)
        emit("lib/libObj.so", pp_valuecheck_patch.patch(lo, hlg=hlg) if color_gamut or gamma_slog else lo)
    caution, delta = patch_caution((a / "lib/CautionConfig.so").read_bytes(), ids)
    textos_fn = {f: (ids[M.SETTINGS[f].label] & 0xFFFF, ids[FN_AYUDA.get(f, fn_lut_listas.AYUDA)] & 0xFFFF) for f in FN_TREES}
    if FN_TREES:                                     # G86-B/G102: los nodos de FN_TREES elegibles en las 12 ranuras Fn
        caution = fn_lut_listas.patch_caution(caution, [textos_fn[f] for f in FN_TREES])
    if RUEDA:                                        # G101/G102: y los de RUEDA en la lista de asignación de la rueda de control
        caution = rueda_film.patch_caution(caution, [textos_fn[f] for f in RUEDA])
    emit("lib/CautionConfig.so", caution)
    # G28: la UI usa la copia del gestor de procesos que lleva viewUnified2.so (cmn_view_processDataMgr.so no se carga) y los pids originales los usa casi todos algún nodo:
    # los ajustes de PP van en pids nuevos (espacio ampliado en pid_space.py); Silent conserva el 0x12 (descriptor propio sobre la tabla original, antes de copiarla).
    vu2 = A.patch((a / "lib/viewUnified2.so").read_bytes(), [*entradas_previas, *([delta] if isinstance(delta, int) else delta)])   # entradas_previas: p. ej. Silent (0xEB0) en el CFW completo
    if silent:
        vu2 = silent_descriptor.patch(vu2, silent_descriptor.TABLA_D_VU2, silent_descriptor.DESC_EFCS_VU2)
    vu2 = pid_space.patch(vu2, ajustes, gris_efcs=silent)
    vu2 = fn_lut_listas.patch_vu2(vu2, len(FN_TREES)) if FN_TREES else vu2
    if RUEDA:                                        # G101/G102: pid 0xdc con los valores nuevos y, con ellos, sus nodos en ViewStlrec/ViewMovieRecPatch (y ViewTriDial de vu7)
        orig_c = (a / "lib/CautionConfig.so").read_bytes()
        ref = _va(orig_c, "cmnViewSettingNodeRootAelWShutter") - _va(orig_c, rueda_film.SIMBOLO)       # nodos respecto al símbolo que importan vu2/vu7
        d_iso = {rueda_film.VALORES[k]: FN_DELTAS[FN_TREES.index(f)] + ref for k, f in enumerate(RUEDA)}
        vu2 = rueda_film.patch_vistas(rueda_film.patch_descriptor(vu2, tuple(d_iso)), rueda_film.SITIOS_VU2, d_iso)
        emit("lib/viewUnified7.so", rueda_film.patch_vistas((a / "lib/viewUnified7.so").read_bytes(), (rueda_film.SITIO_VU7,), d_iso))
    if SD_USERLAND:                                  # G89: hilo del userland que lee los .cube de la SD (DT_INIT → lutsd_hilo), independiente de los demás parches
        import lut_sd_vu2
        vu2 = lut_sd_vu2.patch(vu2)
    emit("lib/viewUnified2.so", vu2)
    if FN_TREES:                                     # G86/G102: hijos 39… de la raíz Fn con los valores fn_lut_menu.VALORES (nodos en FN_DELTAS, relativos a RootAelWShutter)
        orig = (a / "lib/CautionConfig.so").read_bytes()
        emit("lib/viewUnified4.so", fn_lut_menu.patch_vu4((a / "lib/viewUnified4.so").read_bytes(), [fn_lut_menu.delta_respecto_memoryrecall(orig, d) for d in FN_DELTAS]))
    en_b = uxc_strings.parse((b / "share/app/string_english.uxc").read_bytes())[2]
    inv = {}
    for rid, t in sorted(en_b.items()):
        inv.setdefault(t, rid)
    for f in sorted((a / "share/app").glob("string_*.uxc")):
        if f.name.endswith("_guide.uxc"):
            continue
        try:
            head, _, recs = uxc_strings.parse(f.read_bytes())
            assert uxc_strings.build(head, recs) == f.read_bytes()
        except AssertionError:
            continue
        try:
            recs_b = uxc_strings.parse((b / "share/app" / f.name).read_bytes())[2]
        except (AssertionError, FileNotFoundError):
            recs_b = {}
        assert not set(libres) & set(recs), f"ranura ocupada en {f.name}"
        for t, i in ids.items():
            recs[i] = recs_b.get(inv.get(t), t) if inv.get(t) else t
        emit(f"share/app/{f.name}", uxc_strings.build(head, recs))
        manifest["idiomas"].append(f.name + ("" if recs_b else " (inglés)"))
    manifest["ids"] = {t: hex(i) for t, i in ids.items()}
    manifest["pids"] = {k: hex(M.PIDS[i]) for i, k in enumerate(M.SETTINGS)}
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    (dest / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in manifest["parcheados"].items()))


def sin_acciones():
    """Quita Copy y Reset del menú: sin `patch_actions` el despachador de `libObj` (0x4cfb9c) manda sus eventos 0x41/0x42 al error 0x4d02b8."""
    for k in ("copy", "reset"):
        M.SETTINGS.pop(k, None)  # idempotente: `partir` ya puede haberlos quitado
    M.TREE[2][:] = M.paginar([x for x in M.ORDEN if x in M.SETTINGS])


def _reducir(s, maximo):
    """`maximo` valores: simétricos alrededor del neutro de fábrica (`pp_factory.NEUTRO`) con los extremos del lado más corto cuando hay rango a ambos lados
    (±7 → −7, −5, −2, 0, +2, +5, +7); si no, repartidos por todo el rango con el neutro en lugar del más cercano."""
    vals = [v for _, v in s.opciones]
    neutro = pp_factory.NEUTRO.get((s.clave - 0x1F8) // 4, 0)
    m, a = maximo // 2, min(neutro - vals[0], vals[-1] - neutro)
    if maximo % 2 and a >= m and neutro in vals:
        quiero = [neutro + round(a * j / m) for j in range(-m, m + 1)]
        return tuple(o for o in s.opciones if o[1] in quiero)
    ops = [s.opciones[round(i * (len(s.opciones) - 1) / (maximo - 1))] for i in range(maximo)]
    vals = [v for _, v in ops]
    if neutro not in vals and any(v == neutro for _, v in s.opciones):
        cerca = min(range(maximo), key=lambda i: abs(vals[i] - neutro))
        ops[cerca] = next(o for o in s.opciones if o[1] == neutro)
    return tuple(ops)


def partir(maximo=M.OPCIONES_POR_LISTA):
    """G36: la lista de opciones de la clase Normal no pasa de la 7.ª (cámara, 3.77) y con 13 páginas (3.78) el menú se colgaba al entrar; se deja ≤ 6 páginas como
    el 3.77: sin Copy/Reset (los valores de fábrica ya los carga `ppinit`), los numéricos con `maximo` valores (`_reducir`) y los enumerados más largos partidos en filas
    con la misma clave/evento/lectura: por grupos con nombre (`M.PARTES`, G102: «Gamma» / «Gamma Log», …) o, si no hay, equilibradas («Ajuste primera/última»).
    La spec, el orden y los pids se rehacen en el sitio (main y build_nodes guardan sus referencias)."""
    for k in ("copy", "reset"):
        M.SETTINGS.pop(k, None)
    nuevos, orden = {}, []
    for k in [x for x in M.ORDEN if x in M.SETTINGS] + [x for x in M.SETTINGS if x not in M.ORDEN]:
        s = M.SETTINGS[k]
        if len(s.opciones) > maximo and all(t.lstrip("+-").isdigit() for t, _ in s.opciones):
            s = replace(s, opciones=_reducir(s, maximo))
        if len(s.opciones) <= maximo:
            nuevos[k] = s
            orden.append(k)
            continue
        if k in M.PARTES:
            grupos, i = [], 0
            for j, (et, n) in enumerate(M.PARTES[k]):
                ops = s.opciones[i:i + n] if n else s.opciones[i:]
                i += len(ops)
                if ops:
                    grupos.append((k if j == 0 else f"{k}_{j + 1}", et, ops))
            assert i == len(s.opciones), k
        else:
            n = -(-len(s.opciones) // maximo)
            cortes = [len(s.opciones) * i // n for i in range(n + 1)]
            grupos = [(f"{k}_{i + 1}", f"{s.label} {s.opciones[cortes[i]][0]}/{s.opciones[cortes[i + 1] - 1][0]}", s.opciones[cortes[i]:cortes[i + 1]]) for i in range(n)]
        for kid, et, ops in grupos:
            assert len(ops) <= maximo, (kid, len(ops))
            nuevos[kid] = replace(s, id=kid, label=et, opciones=ops)
            orden.append(kid)
    M.SETTINGS.clear()
    M.SETTINGS.update(nuevos)
    M.TREE[2][:] = M.paginar(orden)
    M.PIDS[:] = range(pid_space.PID_PRIMERO, pid_space.PID_PRIMERO + len(nuevos))


def configurar(sat=False, gam=False, col=False, acc=False, hlg=False, fn_pp=False, maximo=M.OPCIONES_POR_LISTA):
    """Ajusta la spec según las opciones (como la línea de órdenes) y devuelve los argumentos con nombre de `main`.
    `fn_pp` (G102): los ajustes `M.FN_COMPLETOS` también como nodos del menú Fn (FN_TREES): el mismo ajuste si su fila quedó entera; si se partió o redujo,
    una copia completa «fn_<id>» con pid propio. `maximo` = opciones por fila antes de partir (G102: 99 = filas enteras; el arnés recorre listas de 31 sin tope)."""
    if not acc:
        sin_acciones()
    if gam:        # ITU709(800%), S-Log2 y S-Log3: requieren libObj parcheado y las curvas de pp_curves_patch.py (núcleo)
        M.SETTINGS["gamma"] = M.S("gamma", "Gamma", 0x214, M.GAMMA_HLG if hlg else M.GAMMA_COMPLETA, "clave+A7S convertValueIdToBackupValue+parche libObj (opt-in)")
    if sat:        # −32…+32 solo si se parchea libObj; ojo: el núcleo toma toda saturación < −7 como blanco y negro (G27)
        M.SETTINGS["saturation"] = M.S("saturation", "Saturation", 0x26C, M.num(-32, 32), "clave+parche libObj (opt-in)")
    if col:        # B&W con efecto (Movie + saturación −8), S-Gamut (= Movie, G27 §5) y S-Gamut3(.Cine) (efecto con `pp_curves_patch.py --color`, G27 §6)
        M.SETTINGS["color_mode"] = M.S("color_mode", "Color Mode", M.K(0), M.COLOR_MODE_COMPLETO, "clave+VALUEID+parche libObj (opt-in)")
    completos = {k: M.SETTINGS[k] for k in M.FN_COMPLETOS if k in M.SETTINGS} if fn_pp else {}
    partir(maximo)
    fn = []
    for k, s in completos.items():          # fila entera en el menú: el nodo Fn usa su mismo ajuste (pid); si se partió/redujo, una copia completa «fn_<id>»
        if M.SETTINGS.get(k) != s:
            M.SETTINGS[f"fn_{k}"] = replace(s, id=f"fn_{k}")
            k = f"fn_{k}"
        fn.append(k)
    M.PIDS[:] = range(pid_space.PID_PRIMERO, pid_space.PID_PRIMERO + len(M.SETTINGS))
    if fn_pp:
        FN_TREES[:] = fn
    return {"saturacion_a6300": sat, "gamma_slog": gam, "color_gamut": col, "acciones": acc, "hlg": hlg and gam}


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(*args[:3], **configurar("--saturacion-a6300" in sys.argv, "--gamma-slog" in sys.argv, "--color-gamut" in sys.argv, "--copy-reset" in sys.argv, "--hlg" in sys.argv))
