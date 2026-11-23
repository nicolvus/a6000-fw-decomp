"""G94 — ConvSD (MOV/MON) es 709→601 en la croma y la tabla precalculada por modo iguala vista en vivo y foto."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C
import lut_modos as LM

pytestmark = pytest.mark.skipif(not C.BIN.exists(), reason="falta av-cam.bin")


def test_convsd_de_fabrica_es_croma_709_a_601():
    q0 = np.zeros((405, 3), np.int8)
    out = LM.NODOS + LM.convsd_fabrica(q0) * LM.U
    A = np.linalg.lstsq(np.c_[LM.NODOS, np.ones(405)], out, rcond=None)[0][:3].T
    M = LM.enc(LM.dec(np.eye(3), "709"), "601").T                         # columnas = imagen de cada eje YCbCr 709 en 601
    assert np.allclose(A[1:, 1:], M[1:, 1:], atol=0.006)                   # bloque Cb/Cr; Y lo deforma el recorte a 0…256 del generador


def test_tabla_precalculada_iguala_vista_en_vivo_y_foto():
    x = C.rejilla(13)
    for nom, tope in (("identidad", 0.15), ("pelicula", 0.6)):
        q = C.descompone(C.SINT[nom], usa_M=False, usa_T=False, usa_L=True, metodo="mc").q
        e = {k: v.mean() for k, v in LM.fidelidad(q, x).items()}
        assert e["precalculada"] < tope < e["convsd_fabrica"] < e["misma_tabla"]
