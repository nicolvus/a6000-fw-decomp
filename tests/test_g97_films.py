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


def test_menu_cabe_y_numera_los_38():
    a = FU.ajustes()
    assert len(FU.orden()) == 38 == len(set(FU.orden()))
    assert all(len(x.opciones) <= 7 for x in a) and len({x.backup for x in a} | {FU.ACK_ID}) == len(a) + 1
    assert all(len(t) <= 12 for x in a for t, _ in x.opciones)


def test_userland_primera_vez_limpia_y_elige_la_ultima_fila(compilado):
    bk = FU.Backup()
    for r in range(len(FU.FILAS)):
        _fila(bk, r, 3 % len(FU.ajustes()[r].opciones))           # restos de otro CFW en los ids libres
    pasos = [None, lambda b: _fila(b, 1, 3), None, lambda b: _fila(b, 0, 2), None, lambda b: _fila(b, 0, 0), None, lambda b: _fila(b, 1, 0), None]
    vistos = []

    def mira(b):
        vistos.append((b.lee(FU.ACK_ID)[0], b.lee(FU.BK_ID)[5]))
    pasos = [p for q in pasos for p in (q, mira)]
    bk = FU.emula(bk, compilado, pasos)
    assert all(bk.lee(FU.ajustes()[r].backup)[0] == 0 for r in range(2, len(FU.FILAS)))   # primera vez: filas a 0
    b1 = FU.bases()[1]
    esperado = [(0, 0), (b1 + 3, b1 + 3), (b1 + 3, b1 + 3), (2, 2), (2, 2), (b1 + 3, b1 + 3), (b1 + 3, b1 + 3), (0, 0), (0, 0)]
    assert vistos == esperado
    assert bk.lee(FU.BK_ID) == FU.blob_esperado(0, NPZ)


def test_userland_blob_de_un_look_y_sin_reescrituras(compilado):
    bk = FU.Backup()
    bk.ids[FU.BK_ID] = FU.blob_esperado(0, NPZ)                     # ya hay blob FILM: no es la primera vez
    _fila(bk, 6, 2)                                                 # Fuji Sim 1 → Classic Chr.
    bk = FU.emula(bk, compilado, [None, None, None])
    look = FU.bases()[6] + 2
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


def test_avcam_curva_tras_la_gamma(parcheado):
    import film_patch as FP
    import tono_post
    img = C.BIN.read_bytes()
    base = list(tono_post.emula(img, 0, bd5=0))
    assert FP.emula_curva(parcheado, 0, None) == base                               # Off: la función original
    z = np.load(NPZ)
    look = next(n for n, i in enumerate(FU.orden(), 1) if str(z["curva"][[str(x) for x in z["ids"]].index(i)]) != "sin_T")
    blob = FU.blob_esperado(look, NPZ)
    T = struct.unpack_from("<1024H", blob, FU.OFF_T)
    assert FP.emula_curva(parcheado, look, blob) == [T[min(v, 1023)] for v in base]
    sin_t = bytearray(blob)
    sin_t[9] = 0
    assert FP.emula_curva(parcheado, look, bytes(sin_t)) == base


def test_avcam_solo_ganchos_y_zona_a(parcheado):
    import avcam_dinamico as D
    import film_patch as FP
    img = C.BIN.read_bytes()
    dif = [i + FP.BASE for i, (a, b) in enumerate(zip(img, parcheado)) if a != b]
    ganchos = [h[0] for h in FP.L.HOOKS] + [FP.L.HOOK_MAQ[0], *FP.HOOKS_T]
    assert all(D.ZONA_A[0] <= a < D.ZONA_A[1] or any(g <= a < g + 4 for g in ganchos) for a in dif)
