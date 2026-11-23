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


RAM = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"     # no versionado (1 GiB)


def test_convsd_activable():
    assert not LM.convsd_activable(bytes([0, 1, 0xFF]), 0x40)
    assert LM.convsd_activable(bytes([0x12]), 0) and not LM.convsd_activable(bytes([0x32]), 0)
    assert LM.convsd_activable(b"", 0x02)


@pytest.mark.skipif(not RAM.exists(), reason="falta el volcado de RAM viva")
def test_convsd_inactivo_en_la_ram_viva():
    with RAM.open("rb") as f:
        lee = lambda va, n: (f.seek(va - 0x43541000 + 0x03541000), f.read(n))[1]     # virtual 0x43… = físico 0x83…
        assert lee(0x44021084, 4) == (0x43E964A4).to_bytes(4, "little")              # GOT vivo de `FUN_437a1d14`
        assert lee(0x4402555C, 4) == (0x43F78DD2).to_bytes(4, "little")              # GOT vivo de `FUN_437a4358`
        ids, caps = lee(LM.IDS_COLOR, 16), lee(LM.CAPS, 1)[0]
    assert set(ids) <= {0, 1, 0xFF} and not LM.convsd_activable(ids, caps)


def test_tabla_precalculada_iguala_vista_en_vivo_y_foto():
    x = C.rejilla(13)
    for nom, tope in (("identidad", 0.15), ("pelicula", 0.6)):
        q = C.descompone(C.SINT[nom], usa_M=False, usa_T=False, usa_L=True, metodo="mc").q
        e = {k: v.mean() for k, v in LM.fidelidad(q, x).items()}
        assert e["precalculada"] < tope < e["convsd_fabrica"] < e["misma_tabla"]
