"""E25-17 — verificadores de la investigación de exposición larga (offline, solo lectura del firmware 3.21).

Cubre: bytes citados en el informe, aritmética del productor nativo (emulado), invariantes de la planificación
multicuadro y la existencia de los entregables. No prueba comportamiento físico del sensor.
"""
import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e25_17"))
sys.path.insert(0, str(ROOT / "scripts/e25_16"))

pytest.importorskip("unicorn")
pytest.importorskip("capstone")
import emular_productor as EP
import evidencia as EV
from emu_core import BASE, FW, Emu

FW_OK = FW.exists()
pytestmark = pytest.mark.skipif(not FW_OK, reason="firmware fw321 no disponible")

PRODUCTOR = json.loads((ROOT / "analysis/e25-17/productor.json").read_text()) if FW_OK else {}
EVID = json.loads((ROOT / "analysis/e25-17/evidencia.json").read_text()) if FW_OK else {}
REPORT = ROOT / "docs/capture/e25-17-bulb-exposicion-electronica-larga.md"


@pytest.fixture(scope="module")
def emu():
    e = Emu()
    e.mu.mem_write(EP.MOD, FW.read_bytes()[EP.MOD - BASE:EP.MOD - BASE + 0x40])
    return e


def test_evidencia_bytes_y_cadenas_sin_fallos():
    assert EVID["fallos"] == 0
    assert len(EVID["sitios"]) >= 35
    assert all(f["ok"] for f in EVID["sitios"] + EVID["cadenas"])
    assert "SetRead_ZAF" in EVID["setread_zaf_cadena"]


def test_evidencia_regenerable():
    # la comprobación viva coincide con el JSON archivado
    for a, esp, _mn, _h in EV.SITIOS:
        assert EV.rd(a, len(esp) // 2).hex() == esp, hex(a)


@pytest.mark.parametrize("nombre", list(EP.SPEEDS))
def test_invariante_planificacion_pred0(nombre):
    f = PRODUCTOR["filas"]["pred0"][nombre]
    vts, suelo = PRODUCTOR["vts"], PRODUCTOR["suelo"]
    total = max(suelo + f["lineas"], vts)
    assert f["r5_shd"] == total - f["lineas"]                    # exposición = total - shd
    assert f["d8"] + f["svd"] * vts == total                     # cuadro con resto + cuadros de VTS
    assert f["svd"] == max(total // vts - 1, 0)
    # con svd = 0 los tres VTS son el total; con svd > 0 los cuadros intermedios y el último son VTS
    assert f["da"] == f["dc"] == (vts if f["svd"] else total)


def test_tabla_clave_del_informe():
    p = PRODUCTOR["filas"]["pred0"]
    assert (p["1/30"]["r5_shd"], p["1/30"]["svd"]) == (2025, 0)
    assert (p["1/15"]["r5_shd"], p["1/15"]["svd"], p["1/15"]["d8"]) == (1, 0, 4389)
    assert (p["1/8"]["svd"], p["1/8"]["d8"]) == (0, 8225)
    assert p["1 s"]["svd"] == 14 and p["30 s"]["svd"] == 472 and p["30 s"]["svd"] < 4096
    # T047 sigue reproducido por la ley r5 = 4219 - líneas
    assert [p[v]["r5_shd"] for v in ("1/4000", "1/250", "1/60")] == [4203, 3956, 3122]


def test_predicado_uno_suma_un_cuadro():
    a, b = PRODUCTOR["filas"]["pred0"], PRODUCTOR["filas"]["pred1"]
    assert b["1/30"]["svd"] == a["1/30"]["svd"] + 1 and b["1/30"]["r5_shd"] == 6244
    assert b["1 s"]["svd"] == a["1 s"]["svd"] + 1 and b["1 s"]["r5_shd"] == 4220
    for v in a:
        assert a[v]["lineas"] == b[v]["lineas"]                  # record+0xf0 no depende del predicado


@pytest.mark.parametrize("nombre", ["1/60", "1/15", "1 s", "30 s"])
def test_emulacion_viva_coincide_con_json(emu, nombre):
    r = EP.correr(emu, EP.SPEEDS[nombre], EP.VTS, 0)
    j = PRODUCTOR["filas"]["pred0"][nombre]
    assert (r["lineas"], r["r5_shd"], r["svd"], r["d8"]) == (j["lineas"], j["r5_shd"], j["svd"], j["d8"])


def test_svd_cabe_en_12_bits_hasta_30s():
    # ID3/ID4 guardan 12 bit de svd: 30 s necesita 472, BULB de ~4096 cuadros ≈ 262 s por tramo
    assert PRODUCTOR["filas"]["pred0"]["30 s"]["svd"] <= 0xFFF
    assert math.isclose(4096 * 4219 * 15.2e-6, 262.7, rel_tol=0.01)


def test_informe_y_entregables():
    assert REPORT.exists()
    txt = REPORT.read_text()
    for k in ("## 8. Veredictos", "Decisión final: C", "SetRead_ZAF", "bulbFrameCount", "0x438c82fe"):
        assert k in txt
    for f in ("scripts/e25_17/fw.py", "scripts/e25_17/emular_productor.py", "scripts/e25_17/evidencia.py",
              "analysis/e25-17/productor.json", "analysis/e25-17/evidencia.json"):
        assert (ROOT / f).exists(), f
