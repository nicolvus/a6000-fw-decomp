"""FILM-PB-1 (27-11-2026): escenario mínimo del manejador de PlayMovie de libmpr 3.21 en Unicorn.

Se ejecuta desde la raíz del repo:  .venv/bin/python -m pytest reports/evidence/film-pb-1-sub-arnes-20261127 -q
No sustituye a `tests/`: vive en evidence porque es el andamio del informe
reports/film-pb-1-sub-arnes-20261127.md, no una prueba del producto.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

pytest.importorskip("unicorn")
import mpr_pb as M  # noqa: E402

pytestmark = pytest.mark.skipif(not M.LIB.is_file(), reason="libmpr.so de fábrica 3.21 ausente")

ORDEN = 0x4000001D
# puntos de un solo uso propuestos en el informe del 26-11 (§5), verificados aquí
P_GUARDA_A, P_GUARDA_B, P_MOTOR = 0x437C0A, 0x437C3C, 0x437CFC


def _corre(traza=None, **kw):
    t = [] if traza is None else traza
    return M.escenario(traza=t, **kw), t


def test_libmpr_de_fabrica_se_carga_y_ejecuta():
    """El andamio carga la biblioteca y ejecuta una función real (0x447810) sin tocar la cámara."""
    r, _ = _corre()
    assert r["relocs"] == 934 + 2580          # JUMP_SLOT/GLOB_DAT + ABS32 aplicadas
    assert r["pc_error"] is None


def test_estado_del_core_distinto_de_5_da_0x0a():
    r, t = _corre(estado=0)
    assert r["completado"] == {"orden": ORDEN, "tam": 4, "status": 0x0A}
    assert not ({P_GUARDA_A, P_GUARDA_B, P_MOTOR} & set(t))


def test_guarda_a_capacidades_da_0x1a():
    r, t = _corre(capacidad=0)
    assert r["ramas"] == ["guarda A"]
    assert r["completado"] == {"orden": ORDEN, "tam": 4, "status": 0x1A}
    assert P_GUARDA_A in t and P_GUARDA_B not in t and P_MOTOR not in t


def test_guarda_b_contenido_no_soportado_da_0x1a():
    r, t = _corre(contenido=0)
    assert r["ramas"] == ["guarda A", "guarda B"]
    assert r["completado"] == {"orden": ORDEN, "tam": 4, "status": 0x1A}
    assert P_GUARDA_B in t and P_GUARDA_A not in t and P_MOTOR not in t


def test_fallo_del_motor_traducido_por_0x7111b0_da_0x1a():
    """El traductor se ejecuta de verdad: 0x1C00001A -> 0x1A (mismo mapa que el informe del motor)."""
    r, t = _corre(motor=0x1C00001A)
    assert r["ramas"] == ["guarda A", "guarda B"]
    assert r["completado"] == {"orden": ORDEN, "tam": 4, "status": 0x1A}
    assert P_MOTOR in t and P_GUARDA_A not in t and P_GUARDA_B not in t


def test_traductor_7111b0_mapea_1c00001a_a_1a():
    assert M.traduce(0x1C00001A) == 0x1A
    assert M.traduce(0x00000000) == 0


def test_camino_feliz_no_llama_a_la_finalizacion():
    r, t = _corre()
    assert r["completado"] is None and r["pc_error"] is None
    assert not ({P_GUARDA_A, P_GUARDA_B, P_MOTOR} & set(t))


def test_el_manejador_acepta_el_mensaje_real_de_fealp_playmovie():
    """FeaIf::PlayMovie (0x44EE9C) real arma el mensaje de 0x8C y el manejador lo consume."""
    msg = M.mensaje_real()
    assert len(msg) == M.TAM_MSG == 0x8C
    assert msg[0x00:0x04] == (0x2A).to_bytes(4, "little")   # parámetro del API
    assert msg[0x1C] == 1 and msg[0x60] == 1                # válidos de RSMPoint y PlayMovieCtrl
    assert msg[0x64] == 1 and msg[0x68] == 0x11             # primer y segundo campo del PlayMovieCtrl
    r, _ = _corre(mensaje=msg, contenido=0)
    assert r["completado"]["orden"] == ORDEN and r["completado"]["status"] == 0x1A
