#!/usr/bin/env python3
"""G23 — paquete de prueba «Gamma de Picture Profile» para la A6000 fw3.21 (solo ficheros; no toca la cámara).

Crea una carpeta «Picture Profile» → páginas → ajustes (nodos de datos puros, sin código; `PAGINAS_PP` define cuántas páginas y qué ajuste lleva cada una) y reutiliza el ajuste oculto `AfIlluminator` (raíz `cmnViewSettingNodeRootAfIlluminator`) como menú «Gamma» con 7 opciones y lo cablea al descriptor
de `pp_gamma_descriptor.py` (ProcessId 0x3c: `@M00B` 0x40/clave 0x214, lectura 0x49/0x216). Sin código nuevo:
  lib/cmn_view_processDataMgr.so  descriptor de Gamma (pp_gamma_descriptor.py)
  lib/CautionConfig.so            listas de propiedades de 8 nodos (editadas en sitio, mismo tamaño), `NumOf…AfIlluminatorDefault` = 7 y array de hijos
                                  nuevo en un segmento RW (7 R_ARM_ABS32; la cuenta del constructor se lee de `NumOf` en tiempo de ejecución)
  lib/viewUnified2.so             la raíz como entrada nueva en las 5 páginas (add_menu_entry.py, delta = raíz − `RootAelWShutter`)
  share/app/string_<idioma>.uxc   textos nuevos (Gamma, Still, ITU709, Cine1–4) en ranuras libres (solo esquema latino)
Los 7 nodos hijos son nodos ociosos de ajustes ocultos (AfIlluminator, CtrlDialWheelSetup, WheelLock, AfTrackingSpeed1).
Uso: build_pp_gamma_menu.py DIR_DEV_A6000 DIR_DEV_A6300 SALIDA
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import add_menu_entry as A
import pp_gamma_descriptor
import uxc_strings

PID, RES = pp_gamma_descriptor.PID, 0x0204_0000
ROOT_NAME = "AfIlluminator"
# (nodo hijo ocioso, texto): orden del menú = orden de pp_gamma_descriptor.GAMMAS (Movie 4, Still 5, ITU709 3, Cine1–4 6–9)
OPCIONES = (
    ("AfIlluminatorAuto", "movie"), ("AfIlluminatorOFF", "still"), ("CtrlDialWheelSetupFnoWheelShutter", "itu709"),
    ("CtrlDialWheelSetupShutterWheelFno", "cine1"), ("WheelLockLock", "cine2"), ("WheelLockUnLock", "cine3"), ("AfTrackingSpeed1", "cine4"),
)
# textos nuevos: clave → (id en la A6300 o None si es literal, literal)
TEXTOS = {"gamma": (None, "Gamma"), "pp": (None, "Picture Profile"), "still": (0xF6E7, ""), "itu709": (0xF718, ""), "cine1": (0xF6BB, ""), "cine2": (0xF6B9, ""),
          "cine3": (0xF6BA, ""), "cine4": (0xF6BE, "")}
# páginas de la carpeta «Picture Profile» (cada una es un nodo de página): lista de raíces (`cmnViewSettingNodeRoot<nombre>`). Añadir páginas = añadir listas
PAGINAS_PP = [[ROOT_NAME]]
MOVIE_ID = 0xE1B4                       # «Movie» ya existe en el A6000


def sym(d, segs, dyn, name):
    i = A._symbol_index(d, segs, dyn, name.encode())
    symtab = A._off(segs, {t: v for t, v in dyn if t}[6])
    return i, symtab + 16 * i, struct.unpack_from("<III", d, symtab + 16 * i + 4)  # índice, offset de entrada, (st_value, st_size, info)


def free_ids(a: Path, n: int, excluir=()):
    """Ranuras vacías en todos los idiomas latinos, sin referencia 0x0204xxxx en las bibliotecas, de mayor a menor."""
    ocupadas, heads = set(), []
    for f in (a / "share/app").glob("string_*.uxc"):
        if f.name.endswith("_guide.uxc"):
            continue
        try:
            head, _, recs = uxc_strings.parse(f.read_bytes())
            assert uxc_strings.build(head, recs) == f.read_bytes()
        except AssertionError:
            continue
        ocupadas |= set(recs)
        heads.append(len(head))
    refs = set()
    for so in list((a / "lib").glob("*.so*")):
        b = so.read_bytes()
        refs |= {w & 0xFFFF for (w,) in struct.iter_unpack("<I", b[: len(b) // 4 * 4]) if w >> 16 == 0x0204}
    ini = min(heads)
    return [i for i in range(0xF745, 0xE000, -1) if i not in ocupadas and i not in refs and i not in excluir and i - 0xE000 < (ini - 0x10) // 2][:n]


class Segmento:
    """PT_LOAD RW añadido: bloques de palabras con relocaciones (`rel`: índice→'R' = RELATIVE, o índice de símbolo ABS32)."""

    def __init__(self, base_va):
        self.va, self.words, self.rels = base_va, [], []    # base_va = inicio de los bloques (tras .rel.dyn)

    def alloc(self, words, rel=None):
        va = self.va + 4 * len(self.words)
        self.words += list(words)
        for i, r in (rel or {}).items():
            self.rels.append((va + 4 * i, r))
        return va


def patch_caution(data: bytes, ids: dict) -> bytes:
    out = bytearray(data)
    segs = A._segments(data)
    _, dyn = A._dynamic(data, segs)
    lt = lambda k: RES | (MOVIE_ID if k == "movie" else ids[k])
    listas = {f"cmnViewSettingPropertyList{ROOT_NAME}Root": [(0, 0, lt("gamma")), (6, 0, lt("gamma")), (0xB, 1, 2), (0xC, 1, 0), (0xE, 1, PID)]}
    for i, (nodo, k) in enumerate(OPCIONES):
        listas[f"cmnViewSettingPropertyList{nodo}"] = [(0, 0, lt(k)), (6, 0, lt(k)), (0xB, 1, 0), (0xC, 1, 1), (0xF, 1, i), (0x10, 1, i)]
    for name, tri in listas.items():
        _, _, (va, size, _) = sym(data, segs, dyn, name)
        assert size == 12 * len(tri), (name, size)             # mismo tamaño: edición en sitio, sin tocar la cuenta del constructor
        struct.pack_into(f"<{3 * len(tri)}I", out, A._off(segs, va), *[x for t in tri for x in t])
    _, _, (n_va, n_size, _) = sym(data, segs, dyn, f"cmnViewSettingNodesNumOf{ROOT_NAME}Default")
    assert n_size == 4 and struct.unpack_from("<I", data, A._off(segs, n_va))[0] == 2
    struct.pack_into("<I", out, A._off(segs, n_va), len(OPCIONES))
    ai, a_ent, (a_va, a_size, _) = sym(data, segs, dyn, f"cmnViewSettingNodes{ROOT_NAME}Default")
    assert a_size == 8
    tags = {t: v for t, v in dyn if t}
    rel_va, rel_sz = tags[0x11], tags[0x12]
    rel = data[A._off(segs, rel_va):A._off(segs, rel_va) + rel_sz]
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(data) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    # el tamaño de .rel.dyn nuevo depende del nº de relocaciones: se reserva con holgura y se fija al final
    max_rel = 8 * (len(OPCIONES) + 8 * (2 + len(PAGINAS_PP)) + len(PAGINAS_PP) + sum(map(len, PAGINAS_PP)) + 16)
    seg = Segmento(new_va + (rel_sz + max_rel + 15) // 16 * 16)
    arr = seg.alloc([0] * len(OPCIONES), {i: sym(data, segs, dyn, f"cmnViewSettingNode{n}")[0] for i, (n, _) in enumerate(OPCIONES)})
    struct.pack_into("<II", out, a_ent + 4, arr, 4 * len(OPCIONES))       # st_value, st_size del array de hijos de Gamma
    raiz = lambda n: sym(data, segs, dyn, f"cmnViewSettingNodeRoot{n}")[2][0]
    vt = sym(data, segs, dyn, "_ZTV18CmnViewSettingNode")[2][0] + 8
    # nodos nuevos de datos puros: {vtable, hijos, cuenta, props, 0×6}; props = {lista, cuenta} (verificado en memoria con gdb)
    def nodo(tripletas, hijos):
        lst = seg.alloc([x for t in tripletas for x in t])
        kids = seg.alloc(hijos, {i: "R" for i in range(len(hijos))})
        props = seg.alloc([lst, len(tripletas)], {0: "R"})
        return seg.alloc([vt, kids, len(hijos), props] + [0] * 6, {0: "R", 1: "R", 3: "R"})
    paginas = [nodo([(0xB, 1, 0)], [raiz(n) for n in h]) for h in PAGINAS_PP]
    carpeta = nodo([(0, 0, lt("pp")), (6, 0, lt("pp")), (0xB, 1, 0), (0xC, 1, 3)], paginas)
    rel_new = bytearray(rel)
    for va, r in seg.rels:
        rel_new += struct.pack("<II", va, 0x17 if r == "R" else (r << 8) | A.R_ARM_ABS32)
    assert len(rel_new) <= rel_sz + max_rel
    blob = bytearray()
    for w in seg.words:
        blob += struct.pack("<I", w)
    head = bytes(rel_new).ljust(seg.va - new_va - 0, b"\0")
    body = head + blob
    phdr_off = new_off + len(body)
    new_ph = [list(x) for x in segs] + [[1, new_off, new_va, new_va, 0, 0, 6, A.ALIGN]]
    new_ph[-1][4] = new_ph[-1][5] = len(body) + 32 * len(new_ph)
    body += b"".join(struct.pack("<8I", *x) for x in new_ph)
    res = bytearray(bytes(out).ljust(new_off, b"\0") + body)
    struct.pack_into("<I", res, 28, phdr_off)
    struct.pack_into("<H", res, 44, len(new_ph))
    doff, _ = A._dynamic(data, segs)
    for i, (t, _) in enumerate(dyn):
        if t == 0x11:
            struct.pack_into("<I", res, doff + 8 * i + 4, new_va)
        if t == 0x12:
            struct.pack_into("<I", res, doff + 8 * i + 4, len(rel_new))
    return bytes(res), carpeta - raiz("AelWShutter")       # carpeta − RootAelWShutter = delta de add_menu_entry


def main(dev_a, dev_b, dest):
    a, b, dest = Path(dev_a) / "nflasha15_unpacked_unpacked", Path(dev_b) / "nflasha15_unpacked_unpacked", Path(dest)
    (dest / "lib").mkdir(parents=True, exist_ok=True)
    (dest / "share/app").mkdir(parents=True, exist_ok=True)
    manifest = {"originales": {}, "parcheados": {}, "idiomas": []}

    def emit(rel, data):
        (dest / rel).write_bytes(data)
        manifest["originales"][rel] = hashlib.sha256((a / rel).read_bytes()).hexdigest()
        manifest["parcheados"][rel] = hashlib.sha256(data).hexdigest()

    g09 = {0xF3E8, 0xF515, 0xF56A}                                 # ranuras que usa build_silent_menu_test.py
    libres = free_ids(a, len(TEXTOS), g09)
    assert len(libres) == len(TEXTOS), libres
    ids = dict(zip(TEXTOS, libres))
    emit("lib/cmn_view_processDataMgr.so", pp_gamma_descriptor.patch((a / "lib/cmn_view_processDataMgr.so").read_bytes()))
    caution, delta = patch_caution((a / "lib/CautionConfig.so").read_bytes(), ids)
    emit("lib/CautionConfig.so", caution)
    emit("lib/viewUnified2.so", A.patch((a / "lib/viewUnified2.so").read_bytes(), delta))
    english = uxc_strings.parse((b / "share/app/string_english.uxc").read_bytes())[2]
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
        for k, (old, lit) in TEXTOS.items():
            recs[ids[k]] = lit if old is None else recs_b.get(old, english[old])
        emit(f"share/app/{f.name}", uxc_strings.build(head, recs))
        manifest["idiomas"].append(f.name + ("" if recs_b else " (inglés)"))
    manifest["ids"] = {k: hex(v) for k, v in ids.items()}
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    (dest / "SHA256SUMS").write_text("".join(f"{h}  {r}\n" for r, h in manifest["parcheados"].items()))


if __name__ == "__main__":
    main(*sys.argv[1:4])
