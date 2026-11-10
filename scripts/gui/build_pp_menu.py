#!/usr/bin/env python3
"""G23 — paquete de prueba del MENÚ COMPLETO de Picture Profile (A6300/A7S) para la A6000 fw3.21 (solo ficheros; no toca la cámara).

Todo son datos, sin código nuevo (G23 «Más páginas»): `pp_menu_spec.py` define los 26 ajustes (claves de la A7S, rangos del validador de la A6000) y el árbol
carpeta → páginas → ajustes/carpetas. Se construye:
  lib/viewUnified2.so             descriptores (pp_descriptors.py) en ProcessIds inertes (`PIDS`, clase forzada a Normal) dentro de la copia del gestor de procesos (G28)
  lib/CautionConfig.so            nodos de datos puros (raíz+opciones de cada ajuste, carpetas y páginas) en un PT_LOAD RW con relocaciones RELATIVE
  lib/viewUnified2.so             entrada nueva = carpeta «Picture Profile» en las 5 páginas del menú (add_menu_entry.py)
  share/app/string_<idioma>.uxc   textos en ranuras libres (traducción de la A6300 si el inglés coincide; si no, el literal)
Uso: build_pp_menu.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA [--saturacion-a6300] [--gamma-slog] [--color-gamut] [--copy-reset]
Las cuatro opciones parchean `libObj.so` (patch_libobj_pp.py). Sin `--copy-reset` el menú no lleva Copy ni Reset: la `libObj` original rechaza sus eventos 0x41/0x42.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import build_pp_gamma_menu as G
import patch_libobj_pp
import pp_descriptors
import pp_menu_spec as M
import silent_descriptor
import uxc_strings

RES = 0x0204_0000


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
            ops = [nodo([(0, 0, lt(t)), (6, 0, lt(t)), (0xB, 1, 0), (0xC, 1, 1), (0xF, 1, k), (0x10, 1, k)], []) for k, (t, _) in enumerate(s.opciones)]
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
        return seg, build_nodes(seg, vt, ids)

    n_rel = len(run(new_va)[0].rels)                      # el nº de relocaciones no depende de la base
    seg, carpeta = run(new_va + (rel_sz + 8 * n_rel + 15) // 16 * 16)
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
    return bytes(res), carpeta - ref


def main(dev_a, dev_b, dest, saturacion_a6300=False, gamma_slog=False, color_gamut=False, acciones=False, entradas_previas=(), silent=False):
    a, b, dest = Path(dev_a) / "nflasha15_unpacked_unpacked", Path(dev_b) / "nflasha15_unpacked_unpacked", Path(dest)
    (dest / "lib").mkdir(parents=True, exist_ok=True)
    (dest / "share/app").mkdir(parents=True, exist_ok=True)
    manifest = {"originales": {}, "parcheados": {}, "idiomas": []}

    def emit(rel, data):
        (dest / rel).write_bytes(data)
        manifest["originales"][rel] = hashlib.sha256((a / rel).read_bytes()).hexdigest()
        manifest["parcheados"][rel] = hashlib.sha256(data).hexdigest()

    txt = textos()
    libres = G.free_ids(a, len(txt), {0xF3E8, 0xF515, 0xF56A})
    assert len(libres) == len(txt)
    ids = dict(zip(txt, libres))
    ajustes = [pp_descriptors.Ajuste(M.PIDS[i], s.clave, tuple(v for _, v in s.opciones), s.evento) for i, s in enumerate(M.SETTINGS.values())]
    if saturacion_a6300 or gamma_slog or color_gamut or acciones:     # opt-in: ver patch_libobj_pp.py
        lo = (a / "lib/libObj.so").read_bytes()
        lo = patch_libobj_pp.patch(lo) if saturacion_a6300 else lo
        lo = patch_libobj_pp.patch_gamma(lo) if gamma_slog or acciones else lo
        lo = patch_libobj_pp.patch_actions(lo) if acciones else lo
        emit("lib/libObj.so", patch_libobj_pp.patch_bw(patch_libobj_pp.patch_color(lo)) if color_gamut else lo)
    caution, delta = patch_caution((a / "lib/CautionConfig.so").read_bytes(), ids)
    emit("lib/CautionConfig.so", caution)
    # G28: la UI usa la copia del gestor de procesos que lleva viewUnified2.so (cmn_view_processDataMgr.so no se carga): descriptores y clase Normal van ahí
    vu2 = A.patch((a / "lib/viewUnified2.so").read_bytes(), [*entradas_previas, delta])   # entradas_previas: p. ej. Silent (0xEB0) en el CFW completo
    if silent:
        vu2 = silent_descriptor.patch(vu2, silent_descriptor.TABLA_D_VU2, silent_descriptor.DESC_EFCS_VU2)
    vu2 = pp_descriptors.patch(vu2, ajustes, pp_descriptors.TABLA_D_VU2)
    emit("lib/viewUnified2.so", pp_descriptors.clase_normal(vu2, [silent_descriptor.PID_NUEVO, *M.PIDS]))
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
        M.SETTINGS.pop(k)
    M.TREE[2][0][:] = [x for x in M.TREE[2][0] if x not in ("copy", "reset")]


def configurar(sat=False, gam=False, col=False, acc=False):
    """Ajusta la spec según las opciones (como la línea de órdenes) y devuelve los argumentos con nombre de `main`."""
    if not acc:
        sin_acciones()
    if gam:        # ITU709(800%), S-Log2 y S-Log3: requieren libObj parcheado y las curvas de pp_curves_patch.py (núcleo)
        M.SETTINGS["gamma"] = M.S("gamma", "Gamma", 0x214, M.GAMMA_COMPLETA, "clave+A7S convertValueIdToBackupValue+parche libObj (opt-in)")
    if sat:        # −32…+32 solo si se parchea libObj; ojo: el núcleo toma toda saturación < −7 como blanco y negro (G27)
        M.SETTINGS["saturation"] = M.S("saturation", "Saturation", 0x26C, M.num(-32, 32), "clave+parche libObj (opt-in)")
    if col:        # B&W con efecto (Movie + saturación −8), S-Gamut (= Movie, G27 §5) y S-Gamut3(.Cine) (efecto con `pp_curves_patch.py --color`, G27 §6)
        M.SETTINGS["color_mode"] = M.S("color_mode", "Color Mode", M.K(0), M.COLOR_MODE_COMPLETO, "clave+VALUEID+parche libObj (opt-in)")
    return {"saturacion_a6300": sat, "gamma_slog": gam, "color_gamut": col, "acciones": acc}


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    main(*args[:3], **configurar("--saturacion-a6300" in sys.argv, "--gamma-slog" in sys.argv, "--color-gamut" in sys.argv, "--copy-reset" in sys.argv))
