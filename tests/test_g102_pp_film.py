"""G102 — CFW Film + Picture Profile (3.92): menú PP con cada ajuste en una sola fila (todas sus opciones), las mismas listas en el menú Fn y PP en la rueda;
comprobaciones en Unicorn y sobre los ficheros reales del paquete (`build_cfw_film.py build/cfw_film392 --version 3.92 --pp`)."""
import json
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "tests")]
import add_menu_entry as A
import film_userland as FU
import fn_lut_listas as L
import fn_lut_menu as F
import pid_space
import pp_menu_spec as M
import rueda_film as R
import test_g86_fn_lut as T
import test_g101_rueda_film as T101

LIB = T.LIB
needs = T.needs
OUT = ROOT / "build/cfw_film392"
construido = pytest.mark.skipif(not (OUT / "files/lib/viewUnified4.so").is_file(), reason="CFW 3.92 sin construir (build_cfw_film.py build/cfw_film392 --version 3.92 --pp)")
FN = ["film_todas", "sel", "gamma", "color_mode", "black_level", "bg_level", "saturation", "phase", "det_level", "knee_point"]
VALORES_FN = {   # valores de modelo de cada lista completa (= la fila entera del menú)
    "sel": [9, *range(9), 10], "gamma": [v for _, v in M.GAMMA_COMPLETA], "color_mode": [v for _, v in M.COLOR_MODE_COMPLETO],
    "black_level": list(range(-15, 16)), "bg_level": list(range(-7, 8)), "saturation": list(range(-8, 8)), "phase": list(range(-7, 8)),
    "det_level": list(range(-7, 8)), "knee_point": list(range(13)),
}


def _w(img: bytes, va: int, n: int = 1):
    return struct.unpack_from(f"<{n}I", img, A._off(A._segments(img), va))


def _nodo(cau: bytes, va: int):
    """(texto, pid o None, [(texto, 0xf)]) de un `CmnViewSettingNode` de datos."""
    _, kids, n, props = _w(cau, va, 4)
    tri = lambda p: {a: v for a, _, v in (_w(cau, _w(cau, p, 2)[0] + 12 * i, 3) for i in range(_w(cau, p, 2)[1]))}
    t = tri(props)
    ops = [(o[0] & 0xFFFF, o[0xF]) for o in (tri(_w(cau, k, 4)[3]) for k in (_w(cau, kids, n) if n else ()))]
    return t[0] & 0xFFFF, t.get(0xE), ops


def _desc(vu2: bytes, pid: int):
    """(evento, clave, valores) del descriptor con modelo del pid en la tabla ampliada por `pid_space`."""
    d_va = (_w(vu2, pid_space.SITIO_INIT[2])[0] + 0x25D8FE) & 0xFFFFFFFF
    m = _w(vu2, _w(vu2, _w(vu2, d_va + 4 * pid)[0], 19)[6], 9)
    vals = _w(vu2, m[7], m[8] >> 8)
    return m[2], _w(vu2, m[4])[0], [x - (1 << 32) if x >> 31 else x for x in vals]


def _va(img: bytes, nombre: str) -> int:
    import build_pp_gamma_menu as G
    segs = A._segments(img)
    return G.sym(img, segs, A._dynamic(img, segs)[1], nombre)[2][0]


def _spec(maximo: int) -> dict:
    """configurar(fn_pp=True, maximo) en un subproceso (la spec es global)."""
    code = ("import sys, json; sys.path.insert(0, 'scripts/gui'); import build_pp_menu as B, pp_menu_spec as M; "
            f"B.configurar(gam=True, col=True, acc=False, fn_pp=True, maximo={maximo}); "
            "print(json.dumps({'arbol': M.TREE[2], 'fn': B.FN_TREES, 's': {k: [s.label, [t for t, _ in s.opciones], [v for _, v in s.opciones], s.clave] for k, s in M.SETTINGS.items()}}))")
    return json.loads(subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True, capture_output=True, text=True).stdout)


def test_spec_una_fila_por_ajuste_con_todas_las_opciones():
    """Petición del usuario: nada partido; «Picture Profile» de Off a PP10 en una sola fila, y lo mismo con Gamma, Color Mode y los valores (rangos completos).
    Las listas Fn usan los mismos ajustes (sin copias). ≤ 6 páginas de 6 filas (el 3.78 con 13 se colgaba)."""
    d = _spec(99)
    s, arbol = d["s"], d["arbol"]
    filas = [x for p in arbol for x in p]
    assert len(arbol) <= 6 and all(len(p) <= 6 for p in arbol) and sorted(filas) == sorted(s) and len(filas) == 32
    assert d["fn"] == FN[1:] and set(d["fn"]) <= set(filas)
    assert s["sel"][:2] == ["Picture Profile", ["Off", *(f"PP{k}" for k in range(1, 11))]]
    assert s["gamma"][1] == [t for t, _ in M.GAMMA_COMPLETA] and s["color_mode"][1] == [t for t, _ in M.COLOR_MODE_COMPLETO]
    for k, vals in VALORES_FN.items():
        assert s[k][2] == vals, k
    assert s["wb_lb"][2] == list(range(-9, 10)) and s["knee_slope"][2] == list(range(-5, 6)) and s["det_limit"][2] == list(range(8))
    assert len({s[k][0] for k in filas}) == len(filas) and filas[:2] == ["sel", "gamma"]


def test_spec_partida_con_nombres_si_se_pide_tope_7():
    """Con `maximo=7` (como el 3.79) los enumerados largos se parten en grupos con nombre y las listas Fn son copias completas «fn_<id>»."""
    d = _spec(7)
    s, filas = d["s"], [x for p in d["arbol"] for x in p]
    assert all(len(s[k][1]) <= 7 for k in filas) and len(d["arbol"]) <= 6
    assert s["sel_2"][:2] == ["Picture Profile 7-10", ["PP7", "PP8", "PP9", "PP10"]] and s["gamma_2"][0] == "Gamma Log"
    assert s["color_mode_2"][1] == ["S-Gamut", "S-Gamut3.Cine", "S-Gamut3"] and s["saturation"][2] == [-7, -5, -2, 0, 2, 5, 7]
    assert d["fn"] == [f"fn_{k}" for k in FN[1:]] and all(s[f"fn_{k}"][2] == v for k, v in VALORES_FN.items())


@needs
@pytest.mark.parametrize(("lib", "sitio", "reg_obj", "reg_got", "campo"), T101.VISTAS)
def test_rueda_con_dos_valores_film_9_y_pp_10(lib, sitio, reg_obj, reg_got, campo):
    orig = (LIB / lib).read_bytes()
    nuevo = R.patch_vistas(orig, (R.SITIO_VU7,) if lib == "viewUnified7.so" else R.SITIOS_VU2, {9: 0x1110, 10: 0x2220})
    for v in (0, 1, 7, 8, 11, 12, 13, 14, 15, 0xFF):
        assert T101._nodo(orig, sitio, v, reg_obj, reg_got, campo)[0] == T101._nodo(nuevo, sitio, v, reg_obj, reg_got, campo)[0], v
    for v, d in ((9, 0x1110), (10, 0x2220)):
        nodo, falsos = T101._nodo(nuevo, sitio, v, reg_obj, reg_got, campo)
        assert nodo == falsos[R.SIMBOLO] + d, (hex(sitio), v)


@needs
def test_despachador_fn_con_diez_hijos_conserva_los_valores_originales():
    orig = (LIB / "viewUnified4.so").read_bytes()
    nuevo = F.patch_vu4(orig, list(range(0x100, 0x100 + 10 * 0x40, 0x40)))
    antes = {v: T._srnum(orig, v) for v in range(F.TBH_N)}
    despues = {v: T._srnum(nuevo, v) for v in range(F.TBH_N)}
    assert {v: despues[v] for v in F.VALORES} == {v: 0x27 + k for k, v in enumerate(F.VALORES)}
    assert all(antes[v] is None for v in F.VALORES)
    assert {v: s for v, s in despues.items() if v not in F.VALORES} == {v: s for v, s in antes.items() if v not in F.VALORES}
    assert struct.unpack_from("<H", nuevo, F.MOVS_N)[0] == 0x2200 | 48
    with pytest.raises(ValueError):
        F.patch_vu4(orig, list(range(len(F.VALORES) + 1)))


@needs
def test_ids_libres_de_las_listas_fn_no_los_usa_el_a6000():
    """Los 11 ids de `IDS_LIBRES_1` (y +1 en las ranuras 2…12) no aparecen en ninguna opción de las 12 listas Type08 del A6000."""
    import re

    import test_g87_fn_asignacion as T87
    cau = T87.Lib((LIB / "CautionConfig.so").read_bytes())
    for n in L.RANURAS:
        _, base, tam = cau.sym[f"cmnViewSettingNodesCustomFunction{n}Type08"]
        usados = set()
        for k in range(tam // 4):
            suf = re.sub(r"^cmnViewSettingNodeCustomFunction\d+(CustomFunction\d+)?", "", cau.names[cau.rel[base + 4 * k] >> 8])
            pl = cau.sym[f"cmnViewSettingPropertyListFnFunctionCustomFunction{n}{suf}"]
            v = cau.u(pl[1], pl[2] // 4)
            usados.add(next(v[3 * j + 2] for j in range(pl[2] // 12) if v[3 * j] == 0xF))
        assert not usados & {L.id_en(n, k) for k in range(len(L.IDS_LIBRES_1))}, n


@pytest.fixture(scope="module")
def cfw():
    import uxc_strings
    d = OUT / "files/lib"
    libs = {n: (d / f"{n}.so").read_bytes() for n in ("CautionConfig", "viewUnified2", "viewUnified4", "viewUnified7", "libObj")}
    en = uxc_strings.parse((OUT / "files/share/app/string_english.uxc").read_bytes())[2]
    man = json.loads((OUT / "pp/MANIFEST.json").read_text())
    return libs, en, {k: int(v, 16) for k, v in man["pids"].items()}


def _hijos_fn(libs):
    vu4, cau = libs["viewUnified4"], libs["CautionConfig"]
    lit = ((F.LIT_LDR + 4) & ~3) + 0xBC
    arr = (struct.unpack_from("<I", vu4, lit)[0] + F.LIT_ADD + 4) & 0xFFFFFFFF
    ref = _va(cau, "cmnViewSettingNodeRootMemoryRecallFn")
    return [(ref + struct.unpack_from("<i", vu4, A._off(A._segments(vu4), arr + 4 * (38 + k)))[0]) & 0xFFFFFFFF for k in range(len(FN))]


@construido
def test_cfw_392_menu_fn_diez_listas_completas(cfw):
    """Valor de asignación → SRNum → hijo 39+k de la raíz Fn → nodo con el pid del ajuste completo; su descriptor tiene todos los valores en el orden de las opciones."""
    libs, en, pids = cfw
    cau, vu2, vu4 = libs["CautionConfig"], libs["viewUnified2"], libs["viewUnified4"]
    assert struct.unpack_from("<H", vu4, F.MOVS_N)[0] == 0x2200 | (38 + len(FN))
    for k, (v, nodo) in enumerate(zip(F.VALORES, _hijos_fn(libs))):
        assert T._srnum(vu4, v) == 0x27 + k
        texto, pid, ops = _nodo(cau, nodo)
        assert pid == pids[FN[k]] and [x for _, x in ops] == list(range(len(ops))), FN[k]
        if FN[k] == "film_todas":
            assert en[texto] == FU.CARPETA and len(ops) == 39
            continue
        evento, clave, vals = _desc(vu2, pid)
        assert evento == 0x40 and vals == VALORES_FN[FN[k]], FN[k]
        assert clave == M.SETTINGS[FN[k]].clave, FN[k]
    textos = [[en[t] for t, _ in _nodo(cau, n)[2]] for n in _hijos_fn(libs)]
    assert textos[1] == ["Off", *(f"PP{k}" for k in range(1, 11))]
    assert textos[2] == [t for t, _ in M.GAMMA_COMPLETA] and textos[3] == [t for t, _ in M.COLOR_MODE_COMPLETO]
    assert textos[4][:2] == ["-15", "-14"] and textos[4][15] == "0" and textos[4][-1] == "+15"


@construido
def test_cfw_392_las_12_ranuras_fn_ofrecen_las_diez_listas_antes_de_no_definido(cfw):
    libs, en, _ = cfw
    import test_g87_fn_asignacion as T87
    cau = T87.Lib(libs["CautionConfig"])
    orig = T87.Lib((LIB / "CautionConfig.so").read_bytes())
    for n in L.RANURAS:                                   # GOT original de cada matriz (la reconoce `Lib.lista` en la biblioteca parcheada)
        i = orig.sym[f"cmnViewSettingNodesCustomFunction{n}Type08"][0]
        T87.ORIG_GOT[n] = next(o for o, inf in orig.rel.items() if inf >> 8 == i and inf & 0xFF == 21)
    vu2 = libs["viewUnified2"]
    t1 = list(L.TABLA_1)
    tn = list(L.TABLA_N)
    for k, v in enumerate(F.VALORES):
        t1[L.id_en(1, k)], tn[L.id_en(2, k)] = v, v
    assert vu2.count(L._pack(t1)) == 1 and vu2.count(L._pack(tn)) == 11
    etiquetas = [en[_nodo(libs["CautionConfig"], n)[0]] for n in _hijos_fn(libs)]
    for n in L.RANURAS:
        ents, cnt = cau.lista(n)
        assert cnt == L.N_ORIG + len(FN) and ents[-1][1].endswith("NotSet")
        nuevos = ents[L.POS_NOTSET:L.POS_NOTSET + len(FN)]
        for k, (tipo, va) in enumerate(nuevos):
            assert tipo == "rel"
            texto, _, _ = _nodo(libs["CautionConfig"], va)
            tri = {a: x for a, _, x in (cau.u(cau.u(cau.u(va + 12)[0])[0] + 12 * j, 3) for j in range(6))}
            assert en[texto] == etiquetas[k] and tri[0xF] == L.id_en(n, k)
            assert (t1 if n == 1 else tn)[tri[0xF]] == F.VALORES[k]


@construido
def test_cfw_392_rueda_film_y_picture_profile(cfw):
    """Lista de la rueda: ISO, Balance, Estilo, Efecto, Film, Picture Profile, No definido; tabla [8,0xb,0xd,0xe,0,9,10]; en las tres vistas 9 → nodo Film (hijo 39) y
    10 → nodo PP completo (hijo 40)."""
    libs, en, _ = cfw
    import test_g87_fn_asignacion as T87
    cau = T87.Lib(libs["CautionConfig"])
    orig = T87.Lib((LIB / "CautionConfig.so").read_bytes())
    got = next(o for o, inf in orig.rel.items() if inf >> 8 == orig.sym[R.LISTA][0] and inf & 0xFF == 21)
    arr = cau.u(got)[0]
    assert cau.u(cau.sym[R.CUENTA][1])[0] == 7
    nombres = [en[_nodo(libs["CautionConfig"], cau.u(arr + 4 * k)[0])[0]] if cau.rel[arr + 4 * k] & 0xFF == 23 else None for k in range(7)]
    assert nombres[4:6] == [FU.CARPETA, "Picture Profile"] and nombres[:4] == [None] * 4 and nombres[6] is None
    ops = [{a: x for a, _, x in (cau.u(cau.u(cau.u(cau.u(arr + 4 * k)[0] + 12)[0])[0] + 12 * j, 3) for j in range(6))}[0xF] for k in (4, 5)]
    assert ops == [5, 6]
    vu2, vu7 = libs["viewUnified2"], libs["viewUnified7"]
    tabla = _w(vu2, _w(vu2, R.DESC_RUEDA + 0x20)[0] + 4)[0]
    assert list(_w(vu2, tabla, 7)) == [8, 0xB, 0xD, 0xE, 0, 9, 10] and vu2[A._off(A._segments(vu2), R.DESC_RUEDA) + 0x15] == 7
    hijos = _hijos_fn(libs)
    dist = lambda n: n - _va(libs["CautionConfig"], R.SIMBOLO)
    for img, sitio, ro, rg, campo in ((vu2, R.SITIOS_VU2[0], 5, 4, 0x12C), (vu2, R.SITIOS_VU2[1], 5, 4, 0x138), (vu7, R.SITIO_VU7, 4, 5, 0x130)):
        for v, hijo in ((9, hijos[0]), (10, hijos[1])):
            nodo, falsos = T101._nodo(img, sitio, v, ro, rg, campo)
            assert nodo - falsos[R.SIMBOLO] == dist(hijo), (hex(sitio), v)


@construido
def test_cfw_392_libobj_acepta_todos_los_valores_de_todas_las_filas_y_listas(cfw):
    """Auditoría de modos: cada valor de cada fila del menú PP y de cada lista Fn pasa el validador App2Obj de la `libObj` del paquete (caso = índice del parámetro);
    el selector no pasa de 10 (`pvt_ActionSetPictureProfile`)."""
    from test_g25_gamma_libobj import APP2OBJ_FN, call
    libs, _, pids = cfw
    vu2, lo = libs["viewUnified2"], libs["libObj"]
    vistos = 0
    for k, pid in pids.items():
        if k.startswith("film"):
            continue
        evento, clave, vals = _desc(vu2, pid)
        assert evento == 0x40, k
        if clave == 0x274:
            assert set(vals) <= set(range(11)), k
            continue
        caso = (clave - 0x1F8) // 4
        malos = [v for v in vals if call(lo, APP2OBJ_FN, caso, v)[0] != 1]
        assert not malos, (k, malos)
        vistos += len(vals)
    assert vistos > 300
