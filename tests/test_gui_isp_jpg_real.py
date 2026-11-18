"""E2E-8 / T42 — revelado emulado vs JPG real de la misma escena (DSC03986, ISO 1000). Umbrales = medida + margen pequeño; si el modelo mejora, bajarlos."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/isp"))
import compara_jpg_real as P
import modelo as M

D = ROOT / "analysis/camera-dumps/20261117-traza-S5"
pytestmark = pytest.mark.skipif(not (D / "DSC03986.ARW").is_file(), reason="sin el par RAW+JPG de la traza S5")


@pytest.fixture(scope="module")
def par():
    return P.carga_par(D / "DSC03986.ARW", D / "DSC03986.JPG")


def test_curva_sr2_depende_del_iso(par) -> None:
    std = M.Tablas().curvas["sr2_std"]
    propia = M.Tablas().con_sr2(par["sr2"][0x7802]).curvas["sr2_std"]
    assert par["meta"]["iso"] == 1000 and not np.array_equal(std, propia) and propia[0] > std[0]


def test_delta_e_con_la_curva_del_arw(par) -> None:
    r = P.mide(par, "arw")
    assert r["senal"]["dE76_media"] < 8.0          # MEDIDO 7,47 (píxeles con señal, 15 %)
    assert r["dE76_media"] < 8.5                   # MEDIDO 7,92 (toda la imagen; el suelo de ruido sube por el pie de la curva, NO_VERIFICADO)
    assert abs(r["dL_media"]) < 6


def test_curva_del_arw_mejora_a_la_de_iso100_en_la_senal(par) -> None:
    assert P.mide(par, "arw")["senal"]["dE76_media"] < P.mide(par, "std")["senal"]["dE76_media"] - 3   # MEDIDO 7,47 vs 12,59
