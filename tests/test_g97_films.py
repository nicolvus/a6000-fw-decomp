"""G97 — simulaciones de película: userland (selección y blob «FILM») y cuevas de av-cam (LUT + curva tras la gamma) en Unicorn sobre el código real."""
import struct
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui"), str(ROOT / "scripts")]
import cube_a6000 as C
import film_userland as FU

NPZ = ROOT / "analysis/lut/g97/looks.npz"
pytestmark = pytest.mark.skipif(not (C.BIN.exists() and NPZ.exists()), reason="falta av-cam.bin o looks.npz")


@pytest.fixture(scope="module")
def compilado():
    return FU.compila(NPZ)


@pytest.fixture(scope="module")
def parcheado():
    import film_patch as FP
    return FP.apply_bytes(C.BIN.read_bytes())


def _fila(bk, r, v):
    bk.ids[FU.ajustes()[r].backup] = bytes([v]) + bytes(7)


def _todas(bk, v):
    bk.ids[FU.ajuste_todas().backup] = bytes([v]) + bytes(7)


def _filas(bk):
    return [bk.lee(a.backup)[0] for a in (*FU.ajustes(), FU.ajuste_todas())]


def test_menu_una_fila_por_marca_y_numera_los_38():
    """G102: carpeta «Film Simulation» con una fila por marca y todos sus estilos (la lista vertical no tiene tope de 7, medido en el arnés)."""
    a = FU.ajustes()
    assert len(FU.orden()) == 38 == len(set(FU.orden())) and FU.CARPETA == "Film Simulation"
    assert [x.label for x in a] == ["Kodak", "Fujifilm", "Fujifilm Sim"] and [len(x.opciones) for x in a] == [16, 15, 10]
    assert len({x.backup for x in a} | {FU.ACK_ID}) == len(a) + 1
    assert all(len(t) <= 12 for x in a for t, _ in x.opciones)


def test_userland_primera_vez_limpia_y_elige_la_ultima_fila(compilado):
    bk = FU.Backup()
    for r in range(len(FU.FILAS)):
        _fila(bk, r, 3 % len(FU.ajustes()[r].opciones))           # restos de otro CFW en los ids libres
    pasos = [None, lambda b: _fila(b, 1, 3), None, lambda b: _fila(b, 0, 2), None, lambda b: _fila(b, 0, 0), None, lambda b: _todas(b, 1), None]
    vistos = []

    def mira(b):
        vistos.append((b.lee(FU.ACK_ID)[0], b.lee(FU.BK_ID)[5]))
    pasos = [p for q in pasos for p in (q, mira)]
    bk = FU.emula(bk, compilado, pasos)
    assert all(bk.lee(FU.ajustes()[r].backup)[0] == 0 for r in range(2, len(FU.FILAS)))   # primera vez: filas a 0
    b1 = FU.bases()[1]
    esperado = [(0, 0), (b1 + 3, b1 + 3), (b1 + 3, b1 + 3), (2, 2), (2, 2), (0, 0), (0, 0), (1, 1), (1, 1)]   # un solo look activo: Off en su fila = Off
    assert vistos == esperado
    assert bk.lee(FU.BK_ID) == FU.blob_esperado(1, NPZ)


def test_userland_blob_de_un_look_y_sin_reescrituras(compilado):
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(0, NPZ)                     # ya hay blob FILM: no es la primera vez
    _fila(bk, 2, 2)                                                 # Fujifilm Sim → Classic Chr.
    bk = FU.emula(bk, compilado, [None, None, None])
    look = FU.bases()[2] + 2
    assert FU.orden()[look - 1] == "fuji_sim_classic_chrome"
    assert bk.lee(FU.BK_ID) == FU.blob_esperado(look, NPZ) and bk.lee(FU.ACK_ID)[0] == look
    assert bk.escrituras.count(FU.BK_ID) == 1                       # sondeos sin cambios no escriben la NVRAM


def test_avcam_lut_del_blob_y_fabrica_si_no(parcheado):
    import film_patch as FP
    look = 7
    blob = FU.blob_esperado(look, NPZ)
    z = np.load(NPZ)
    k = [str(i) for i in z["ids"]].index(FU.orden()[look - 1])
    hw = C.empaqueta_hw(z["q"][k], C.BIN.read_bytes())
    for g in (0, 1):
        r, tabla = FP.emula_lut(parcheado, g, look, blob)
        assert r == 0x31000000 and tabla == hw
        assert FP.emula_lut(parcheado, g, 0, blob)[0] == 0x11223344                 # Off
        assert FP.emula_lut(parcheado, g, look + 1, blob)[0] == 0x11223344          # el blob es de otro look
        malo = bytearray(blob)
        malo[0] ^= 1
        assert FP.emula_lut(parcheado, g, look, bytes(malo))[0] == 0x11223344       # sin magia


def test_avcam_curva_por_gamma_extendida_llega_a_la_rejilla_del_hw(parcheado):
    """G98: la curva del look la aplican la rejilla de 96 nodos (FUN_43853200, la que va al HW) y la curva de 512 (FUN_438538e4), por c68[8] + bd5/be1."""
    import film_patch as FP
    import tono_post
    img = C.BIN.read_bytes()
    z = np.load(NPZ)
    look = next(n for n, i in enumerate(FU.orden(), 1) if str(z["curva"][[str(x) for x in z["ids"]].index(i)]) != "sin_T")
    blob = FU.blob_esperado(look, NPZ)
    T = struct.unpack_from("<1024H", blob, FU.OFF_T)
    fab = FP.emula_tono(img, 0, None, entrada=None)
    assert fab["ok"] and FP.emula_tono(parcheado, 0, blob) == fab                      # Off: idéntico a fábrica (Black Gamma incluida)
    sin_bg = FP.emula_tono(img, 0, None, entrada=None, bd1=0)
    on = FP.emula_tono(parcheado, look, blob)
    assert on["ok"] and on["rejilla"] == [T[min(v, 1023)] for v in sin_bg["rejilla"]]
    assert on["curva"] == tono_post.emula(img, 0, tabla=np.array(T), bd5=1, be1=8).tolist()
    sin_t = bytearray(blob)
    sin_t[9] = 0
    assert FP.emula_tono(parcheado, look, bytes(sin_t)) == fab                              # look sin curva: tono de fábrica
    assert FP.emula_tono(parcheado, look + 1, blob) == fab                               # blob de otro look: fábrica


def test_avcam_lut_reintenta_si_el_blob_llega_tarde(parcheado):
    """G98: si el ACK llega antes que el blob, la máquina sigue forzando la recarga (cada 32 pasadas) hasta aplicar el look; luego se queda quieta."""
    import film_patch as FP
    b7, b0 = FU.blob_esperado(7, NPZ), FU.blob_esperado(0, NPZ)
    pasos = [(0, b0)] * 3 + [(7, b0)] * 40 + [(7, b7)] * 45 + [(0, b0)] * 3
    forzadas = [i for i, f in enumerate(FP.emula_maquina(parcheado, pasos)) if f]
    assert forzadas[0] == 3 and any(43 <= i < 43 + 32 for i in forzadas)
    llegada = next(i for i in forzadas if i >= 43)
    assert [i for i in forzadas if llegada < i < 88] == [] and forzadas[-1] == 88


def test_userland_no_da_el_ack_hasta_que_el_blob_esta_escrito(compilado):
    bk = FU.Backup(pierde=2)
    bk.ids[FU.BK_ID] = FU.blob_esperado(0, NPZ)
    _fila(bk, 0, 4)                                                 # Kodak → Kodachrome (look 4)
    vistos = []
    bk = FU.emula(bk, compilado, [lambda b: vistos.append(b.lee(FU.ACK_ID)[0])] * 4)
    assert vistos[0] == 0 and vistos[-1] == 4                      # primer sondeo: blob perdido → sin ACK; después se reintenta
    assert bk.lee(FU.BK_ID) == FU.blob_esperado(4, NPZ)


def test_avcam_solo_ganchos_y_zona_a(parcheado):
    import avcam_dinamico as D
    import film_patch as FP
    img = C.BIN.read_bytes()
    dif = [i + FP.BASE for i, (a, b) in enumerate(zip(img, parcheado)) if a != b]
    ganchos = [h[0] for h in FP.L.HOOKS] + [FP.L.HOOK_MAQ[0], *FP.SITIOS_T]
    assert all(D.ZONA_A[0] <= a < D.ZONA_A[1] or any(g <= a < g + 4 for g in ganchos) for a in dif)


def _rec(bk):
    return [bk.lee(i)[0] for i in FU.REC_ID]


def test_recetas_nativas_cubren_los_38_y_se_codifican_como_recipelab():
    assert set(FU.orden()) == set(FU.RECETA_DE) and set(FU.RECETA_DE.values()) <= set(FU.RECIPELAB)
    p4 = FU.receta_bytes("Kodak Portra 400")                         # Retrato, sat −1, con −1, AWB, A-B +3, G-M +1 (guardado con signo cambiado), EV +2/3, DRO Auto
    assert p4 == [4, -1, -1, 0, 1, FU.NO_TOCA, 3, 3, FU.NO_TOCA, -1, -1, FU.NO_TOCA, 2, 2, 1, 1]
    v5 = FU.receta_bytes("Kodak Vision3 500T (daylight)")            # 3200 K: ranuras K de A-B/G-M y DRO Lv3
    assert v5[4:6] == [14, 32] and v5[7:9] == [FU.NO_TOCA, 0] and v5[14:] == [4, 4]


def test_userland_receta_al_elegir_look_y_devuelve_los_ajustes_del_usuario_en_off(compilado):
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(0, NPZ)
    usuario = [(k * 7 + 3) & 0xFF for k in range(len(FU.REC_ID))]
    for i, v in zip(FU.REC_ID, usuario):
        bk.ids[i] = bytes([v]) + bytes(7)
    fotos = []
    pasos = [lambda b: _fila(b, 0, 6), lambda b: fotos.append(_rec(b)), lambda b: _fila(b, 0, 14), lambda b: fotos.append(_rec(b)),
             lambda b: _fila(b, 0, 0), None, None, None]
    bk = FU.emula(bk, compilado, pasos)
    p4 = FU.receta_bytes("Kodak Portra 400")
    assert fotos[0] == [u if v == FU.NO_TOCA else v & 0xFF for u, v in zip(usuario, p4)]          # Portra 400 puesta; lo que no toca, intacto
    v5 = FU.receta_bytes("Kodak Vision3 500T (daylight)")
    assert fotos[1] == [a if v == FU.NO_TOCA else v & 0xFF for a, v in zip(fotos[0], v5)]         # 500T encima (kelvin y ranuras K)
    assert _rec(bk) == usuario and bk.lee(FU.BK_ID) == FU.blob_esperado(0, NPZ)                  # Off: ajustes del usuario de vuelta


def test_userland_arranque_con_receta_puesta_no_la_reescribe(compilado):
    look = FU.bases()[2] + 2
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(look, NPZ, bytes(range(len(FU.REC_ID))))
    bk.ids[FU.ACK_ID] = bytes([look]) + bytes(7)
    _fila(bk, 2, 2)
    bk = FU.emula(bk, compilado, [None, None])
    assert not set(bk.escrituras) & set(FU.REC_ID) and bk.lee(FU.BK_ID) == FU.blob_esperado(look, NPZ, bytes(range(len(FU.REC_ID))))


def test_fila_todas_tiene_off_y_los_38_en_orden_y_un_id_propio():
    t = FU.ajuste_todas()
    assert [x for x, _ in t.opciones] == ["Off"] + [n for _, looks in FU.FILAS for _, n in looks]
    assert t.backup not in {a.backup for a in FU.ajustes()} | {FU.ACK_ID} and t.pid not in {a.pid for a in FU.ajustes()}


def test_userland_lista_unica_y_filas_sincronizadas(compilado):
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(0, NPZ)
    look = FU.bases()[2] + 2                                        # Classic Chrome, elegido desde la lista única (Fn)
    vistos = []
    pasos = [lambda b: _todas(b, look), lambda b: vistos.append(_filas(b)), lambda b: _fila(b, 0, 14), lambda b: vistos.append(_filas(b)),
             lambda b: _todas(b, 0), lambda b: vistos.append(_filas(b))]
    bk = FU.emula(bk, compilado, pasos)
    filas = [0] * len(FU.FILAS)
    filas[2] = 2
    assert vistos[0] == filas + [look]                              # la fila de su marca lo muestra; las demás en Off
    v5 = FU.bases()[0] + 14                                         # Vision3 500T
    filas = [0] * len(FU.FILAS)
    filas[0] = 14
    assert vistos[1] == filas + [v5]                                # elegido por categoría: la lista única lo sigue
    assert vistos[2] == [0] * (len(FU.FILAS) + 1) and bk.lee(FU.ACK_ID)[0] == 0


def test_userland_arranque_ignora_restos_en_la_lista_unica(compilado):
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(4, NPZ)
    bk.ids[FU.ACK_ID] = bytes([4]) + bytes(7)
    _fila(bk, 0, 4)
    _todas(bk, 24)                                                  # valor de otro CFW (Color Chrome) en el mismo id
    bk = FU.emula(bk, compilado, [None, None])
    assert bk.lee(FU.ACK_ID)[0] == 4 and _filas(bk)[-1] == 4



def test_cfw_film_390_lleva_film_con_los_39_en_el_menu_fn_y_las_12_ranuras():
    """Ficheros del 3.90 construido: ranura Fn → valor 0x26 → hijo 39 → nodo «Film» con pid/Backup de la lista única y Off + los 38 en orden."""
    import add_menu_entry as A
    import build_pp_gamma_menu as G
    import fn_lut_menu as F
    import test_g86_fn_lut as T
    import test_g87_fn_asignacion as T87
    import uxc_strings
    d = ROOT / "build/cfw_film390/files"
    if not (d / "lib/viewUnified4.so").is_file():
        pytest.skip("CFW 3.90 sin construir (build_cfw_film.py build/cfw_film390 --version 3.90)")
    cau_b, vu4, vu2 = ((d / f"lib/{n}.so").read_bytes() for n in ("CautionConfig", "viewUnified4", "viewUnified2"))
    en = uxc_strings.parse((d / "share/app/string_english.uxc").read_bytes())[2]
    segs = A._segments(cau_b)
    _, dyn = A._dynamic(cau_b, segs)
    ref = G.sym(cau_b, segs, dyn, "cmnViewSettingNodeRootMemoryRecallFn")[2][0]
    lit = ((F.LIT_LDR + 4) & ~3) + 0xBC
    arr = (struct.unpack_from("<I", vu4, lit)[0] + F.LIT_ADD + 4) & 0xFFFFFFFF
    nodo = ref + struct.unpack_from("<i", vu4, A._off(A._segments(vu4), arr + 4 * 38))[0]
    rd = lambda va, n: struct.unpack_from(f"<{n}I", cau_b, A._off(segs, va))
    _, kids, n, props = rd(nodo, 4)
    tri = [rd(rd(props, 2)[0] + 12 * i, 3) for i in range(rd(props, 2)[1])]
    t = FU.ajuste_todas()
    assert n == 39 and (0xE, 1, 0xF1) in tri and en[tri[0][2] & 0xFFFF] == "Film"   # 3.90: pid 0xF1 (8 filas por categoría + la lista única) y carpeta «Film»
    ops = []
    for k in rd(kids, n):
        lst, nt = rd(rd(k, 4)[3], 2)
        m = {a: v for a, _, v in (rd(lst + 12 * i, 3) for i in range(nt))}
        ops.append((en[m[0] & 0xFFFF], m[0xF]))
    assert ops == [(x, i) for i, (x, _) in enumerate(t.opciones)]
    cau = T87.Lib(cau_b)
    pat = lambda tab: b"".join(struct.pack("<I", x) for x in tab)
    t1 = struct.unpack_from("<37I", vu2, vu2.index(pat([*T87.TABLA_1[:-1], F.VALOR_LUT])))
    tn = struct.unpack_from("<37I", vu2, vu2.index(pat([F.VALOR_LUT, *T87.TABLA_N[1:]])))
    orig = T87.Lib((T.LIB / "CautionConfig.so").read_bytes())
    for r in range(1, 13):
        i = orig.sym[f"cmnViewSettingNodesCustomFunction{r}Type08"][0]
        got = next(o for o, inf in orig.rel.items() if inf >> 8 == i and inf & 0xFF == 21)   # misma palabra del GOT, ahora RELATIVE a la matriz nueva
        assert cau.rel[got] == 23
        fila = cau.u(cau.u(got)[0], 27)[25]
        m = {a: v for a, _, v in (cau.u(cau.u(cau.u(fila + 12)[0])[0] + 12 * j, 3) for j in range(6))}
        assert en[m[0] & 0xFFFF] == "Film" and (t1 if r == 1 else tn)[m[0xF]] == F.VALOR_LUT
    assert T._srnum(vu4, F.VALOR_LUT) == F.SRNUM_LUT
