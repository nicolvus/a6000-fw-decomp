"""G101 — «Film» en la rueda de control: lista de asignación (CautionConfig), pid 0xdc a 6 opciones (viewUnified2) y elección del nodo con valor 9
en las tres vistas que abren la franja Wheel (ViewStlrec y ViewMovieRecPatch de viewUnified2, ViewTriDial de viewUnified7), en Unicorn sobre los bytes reales."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "tests")]
import add_menu_entry as A
import rueda_film as R
import test_g86_fn_lut as T
import test_g87_fn_asignacion as T87

LIB = T.LIB
needs = T.needs
DELTA = 0x4321                                   # distancia ficticia del nodo «Film» a RootISOSensitivity


def _carga(img: bytes):
    """Mapea la .so como la cargaría ld.so en base 0 y aplica sus relocaciones RELATIVE y ABS32 (símbolos importados → dirección ficticia)."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    segs = A._segments(img)
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    mu.mem_map(0, (top + 0xFFFF) & ~0xFFFF)
    for t, o, v, _, fs, _, _, _ in segs:
        if t == 1:
            mu.mem_write(v, img[o:o + fs])
    lib = T87.Lib(img)
    falsos = {}
    for off, inf in lib.rel.items():
        tipo, s = inf & 0xFF, inf >> 8
        w = struct.unpack("<I", mu.mem_read(off, 4))[0]
        if tipo == 23:
            continue                                                     # base 0: RELATIVE no cambia la palabra
        if tipo in (2, 21) and s:
            sym = falsos.setdefault(lib.names[s], 0x7000_0000 + 0x100 * len(falsos))
            mu.mem_write(off, struct.pack("<I", (sym + (w if tipo == 2 else 0)) & 0xFFFFFFFF))
    return mu, falsos


def _nodo(img: bytes, sitio: int, valor: int, reg_obj: int, reg_got: int, campo: int):
    """Ejecuta desde la carga del byte de la rueda hasta el `str.w` del nodo con `valor` y devuelve lo que guarda la vista en `campo`."""
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_SP
    mu, falsos = _carga(img)
    obj, pila = 0x6000_0000, 0x6100_0000
    mu.mem_map(obj, 0x10000)
    mu.mem_map(pila, 0x10000)
    got = R.got_de(img)
    mu.reg_write(UC_ARM_REG_R0 + reg_got, got)
    mu.reg_write(UC_ARM_REG_R0 + reg_obj, obj)
    mu.reg_write(UC_ARM_REG_SP, pila + 0x8000)
    mu.reg_write(UC_ARM_REG_R0 + 3, valor)
    mu.emu_start(sitio | 1, sitio + R.A_STORE + 4, count=64)
    return struct.unpack("<I", mu.mem_read(obj + campo, 4))[0], falsos


VISTAS = [("viewUnified2.so", R.SITIOS_VU2[0], 5, 4, 0x12C), ("viewUnified2.so", R.SITIOS_VU2[1], 5, 4, 0x138), ("viewUnified7.so", R.SITIO_VU7, 4, 5, 0x130)]


@needs
@pytest.mark.parametrize(("lib", "sitio", "reg_obj", "reg_got", "campo"), VISTAS)
def test_valor_9_da_el_nodo_film_y_los_demas_no_cambian(lib, sitio, reg_obj, reg_got, campo):
    orig = (LIB / lib).read_bytes()
    nuevo = R.patch_vistas(orig, (R.SITIO_VU7,) if lib == "viewUnified7.so" else R.SITIOS_VU2, DELTA)
    for v in (0, 1, 7, 8, 10, 11, 12, 13, 14, 15, 0xFF):
        antes, _ = _nodo(orig, sitio, v, reg_obj, reg_got, campo)
        despues, _ = _nodo(nuevo, sitio, v, reg_obj, reg_got, campo)
        assert antes == despues, (lib, hex(sitio), v)
    antes, _ = _nodo(orig, sitio, 9, reg_obj, reg_got, campo)
    film, falsos = _nodo(nuevo, sitio, 9, reg_obj, reg_got, campo)
    assert antes == 0 and film == falsos[R.SIMBOLO] + DELTA


@needs
def test_pid_0xdc_pasa_a_6_opciones_con_film_valor_9():
    nuevo = R.patch_descriptor((LIB / "viewUnified2.so").read_bytes())
    segs = A._segments(nuevo)
    w = lambda va, n=1: struct.unpack_from(f"<{n}I", nuevo, A._off(segs, va))
    lib = T87.Lib(nuevo)
    assert nuevo[A._off(segs, R.DESC_RUEDA) + 0x15] == 6
    modelo = w(R.DESC_RUEDA + 0x20)[0]
    bk, tabla = w(modelo, 2)
    assert bk == R.BK_RUEDA and list(w(tabla, 6)) == [8, 0xB, 0xD, 0xE, 0, R.VALOR_FILM]
    assert lib.rel[modelo + 4] == 23 and lib.rel[R.DESC_RUEDA + 4] == 23
    assert list(w(w(R.DESC_RUEDA + 4)[0], 6)) == [0xA45] * 6
    with pytest.raises(ValueError):
        R.patch_descriptor(nuevo)


@needs
def test_lista_de_la_rueda_con_film_antes_de_no_definido():
    import uxc_strings
    orig = T87.Lib((LIB / "CautionConfig.so").read_bytes())
    nuevo_b = R.patch_caution((LIB / "CautionConfig.so").read_bytes(), 0x1234, 0x1235)
    nuevo = T87.Lib(nuevo_b)
    i = orig.sym[R.LISTA][0]
    got = next(o for o, inf in orig.rel.items() if inf >> 8 == i and inf & 0xFF == 21)
    assert nuevo.rel[got] == 23
    arr = nuevo.u(got)[0]
    assert nuevo.u(nuevo.sym[R.CUENTA][1])[0] == 6
    nombres = [nuevo.names[nuevo.rel[arr + 4 * k] >> 8] if nuevo.rel[arr + 4 * k] & 0xFF == 2 else "nuevo" for k in range(6)]
    assert nombres[:4] == [f"cmnViewSettingNodeRearWheelRearWheel{x}" for x in ("ISO", "WB", "CS", "PE")]
    assert nombres[4] == "nuevo" and nombres[5].endswith("NotSet")
    nodo = nuevo.u(arr + 16)[0]
    lst, nt = nuevo.u(nuevo.u(nodo + 12)[0], 2)
    tri = {a: v for a, _, v in (nuevo.u(lst + 12 * j, 3) for j in range(nt))}
    assert (tri[0], tri[6], tri[0xB], tri[0xC], tri[0xF], tri[0x10]) == (R.RES | 0x1234, R.RES | 0x1235, 0, 2, 5, 5)
    del uxc_strings


def test_cfw_391_rueda_lleva_al_mismo_nodo_film_de_39_que_el_menu_fn():
    """Ficheros reales del 3.91: opción «Film» de la lista de la rueda (0xf = 5) → tabla del pid 0xdc → 9 → en las tres vistas, el nodo hijo 39 del menú Fn."""
    import build_pp_gamma_menu as G
    import fn_lut_menu as F
    import uxc_strings
    d = ROOT / "build/cfw_film391/files"
    if not (d / "lib/viewUnified7.so").is_file():
        pytest.skip("CFW 3.91 sin construir (build_cfw_film.py build/cfw_film391 --version 3.91)")
    cau_b, vu2, vu4, vu7 = ((d / f"lib/{n}.so").read_bytes() for n in ("CautionConfig", "viewUnified2", "viewUnified4", "viewUnified7"))
    en = uxc_strings.parse((d / "share/app/string_english.uxc").read_bytes())[2]
    segs = A._segments(cau_b)
    _, dyn = A._dynamic(cau_b, segs)
    va = lambda n: G.sym(cau_b, segs, dyn, n)[2][0]
    lit = ((F.LIT_LDR + 4) & ~3) + 0xBC
    arr = (struct.unpack_from("<I", vu4, lit)[0] + F.LIT_ADD + 4) & 0xFFFFFFFF
    film = va("cmnViewSettingNodeRootMemoryRecallFn") + struct.unpack_from("<i", vu4, A._off(A._segments(vu4), arr + 4 * 38))[0]
    cau = T87.Lib(cau_b)
    assert cau.u(film + 8)[0] == 39                                                  # el nodo de 39 opciones (Off + 38)
    orig = T87.Lib((LIB / "CautionConfig.so").read_bytes())
    got = next(o for o, inf in orig.rel.items() if inf >> 8 == orig.sym[R.LISTA][0] and inf & 0xFF == 21)
    op = cau.u(cau.u(got)[0] + 16)[0]
    tri = {a: v for a, _, v in (cau.u(cau.u(cau.u(op + 12)[0])[0] + 12 * j, 3) for j in range(6))}
    assert en[tri[0] & 0xFFFF] == "Film" and tri[0xF] == 5
    s2 = A._segments(vu2)
    tabla = struct.unpack_from("<I", vu2, A._off(s2, struct.unpack_from("<I", vu2, A._off(s2, R.DESC_RUEDA + 0x20))[0] + 4))[0]
    assert struct.unpack_from("<6I", vu2, A._off(s2, tabla))[tri[0xF]] == R.VALOR_FILM
    for img, sitio, ro, rg, campo in ((vu2, R.SITIOS_VU2[0], 5, 4, 0x12C), (vu2, R.SITIOS_VU2[1], 5, 4, 0x138), (vu7, R.SITIO_VU7, 4, 5, 0x130)):
        nodo, falsos = _nodo(img, sitio, R.VALOR_FILM, ro, rg, campo)
        assert nodo - falsos[R.SIMBOLO] == film - va(R.SIMBOLO), hex(sitio)
