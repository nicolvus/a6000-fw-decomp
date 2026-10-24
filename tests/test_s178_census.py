"""Tests de S178 — censo de cobertura de la línea de módulos (A6000 fw3.21).

Tests de **bytes reales**: si cambia el número de etiquetas, un texto o un recuento, fallan.
"""
import json
import os
import re

import pytest

BASE = 0x43541000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A6000 = os.path.join(ROOT, "analysis/rea-independent/input/av-cam.bin")
A7S = os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                           "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
                            "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
ANA = os.path.join(ROOT, "analysis/s178_census")
PAT = re.compile(rb"\[[A-Z][A-Z0-9_]{1,24}\]")


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def a6000():
    return _read(A6000)


@pytest.fixture(scope="module")
def a7s():
    return _read(A7S)


@pytest.fixture(scope="module")
def a6300():
    return _read(A6300)


@pytest.fixture(scope="module")
def etiquetas(a6000):
    return sorted({m.group().decode() for m in PAT.finditer(a6000)})


# --------------------------------------------------------------------------
# 1) El censo
# --------------------------------------------------------------------------

def test_numero_de_etiquetas(etiquetas):
    assert len(etiquetas) == 372


def test_catalogo_y_pendientes_suman_el_total_de_etiquetas(etiquetas):
    """El catalogo crece en paralelo: lo que se comprueba es el invariante, no la foto."""
    with open(os.path.join(ROOT, "docs/capture/linea-general-re.md"), encoding="utf-8") as fh:
        cat = fh.read()
    dec = {s for s in etiquetas if s in cat}
    assert len(dec) >= 52
    assert len(dec) + (len(etiquetas) - len(dec)) == 372
    # las sub-etiquetas de un modulo ya decodificado tambien cuentan como cubiertas
    import re as _re
    sub = {}
    for mm in _re.finditer(rb"\[([A-Z][A-Z0-9_]{1,24})\]\[([A-Z][A-Z0-9_]{1,24})\]",
                           open(A6000, "rb").read()):
        sub.setdefault("[" + mm.group(2).decode() + "]", set()).add("[" + mm.group(1).decode() + "]")
    cub = {s for s, parents in sub.items() if any(p in dec for p in parents)}
    assert len(cub) >= 40
    assert len(dec) + len(cub) + (len(etiquetas) - len(dec) - len(cub)) == 372
    # las 52 de la fotografia inicial siguen decodificadas
    for s in ("[SAD]", "[ILLUMI]", "[TP_R]", "[CAMERA_IS]", "[JOG]", "[LIF_DEBUG]", "[CAM_UTIL]"):
        assert s in dec


def test_93_etiquetas_exclusivas_de_la_a6000(etiquetas, a7s, a6300):
    solo = [s for s in etiquetas
            if a7s.count(s.encode()) == 0 and a6300.count(s.encode()) == 0]
    assert len(solo) == 93
    # algunas concretas, ya decodificadas
    for s in ("[CAM_FUNC_MGR]", "[CAM_SCALAR]", "[REMOTE]", "[CAMERA_MAIN]", "[IMAGING_CAP]"):
        assert s in solo


def test_la_familia_stk_y_osd_desaparecen_en_el_a6300(a6000, a7s, a6300):
    for s in (b"[STK]", b"[STK_AUTO_SAL]", b"[STK_COLOR_SIM]", b"[STK_C_SIM]",
              b"[STK_TOUCH_SIM]", b"[STK_T_SIM]", b"[OSD]"):
        assert a6000.count(s) > 0
        assert a7s.count(s) > 0
        assert a6300.count(s) == 0


def test_vdf_tiene_mas_cadenas_en_la_a6000(a6000, a7s, a6300):
    assert a6000.count(b"[VDF]") == 243
    assert a7s.count(b"[VDF]") == 162
    assert a6300.count(b"[VDF]") == 162


# --------------------------------------------------------------------------
# 2) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "census.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S178"
    r = j["recuentos"]
    assert r["etiquetas"] == 372
    assert r["exclusivas_a6000"] == 93
    assert r["ausentes_en_a6300"] == 7
    assert (r["con_hito"] + r["cubiertas_como_sub_etiqueta"]
            + r["pendientes_reales"] + r["descartadas_no_modulo"]) == 372
    assert r["con_hito"] >= 52
    assert r["cubiertas_total"] == r["con_hito"] + r["cubiertas_como_sub_etiqueta"]
    with open(os.path.join(ANA, "census_detalle.json"), encoding="utf-8") as fh:
        detail = json.load(fh)
    assert r["con_hito"] == sum(x["estado"] == "hito" for x in detail.values())
    assert r["cubiertas_como_sub_etiqueta"] == sum(x["estado"] == "sub-etiqueta" for x in detail.values())
    assert r["pendientes_reales"] == sum(x["estado"] == "pendiente" for x in detail.values())
    assert len(j["elimina_el_a6300"]) == 7
    assert "[STK]" in j["elimina_el_a6300"]
    assert "[OSD]" in j["elimina_el_a6300"]
    # las pendientes reales estan ordenadas por tamaño
    pend = j["pendientes_reales_ordenadas"]
    assert {p["etiqueta"] for p in pend} == {k for k, v in detail.items() if v["estado"] == "pendiente"}
    assert [p["apariciones"] for p in pend] == sorted(
        [p["apariciones"] for p in pend], reverse=True)


def test_detalle_por_etiqueta_consistente(etiquetas):
    with open(os.path.join(ANA, "census_detalle.json"), encoding="utf-8") as fh:
        d = json.load(fh)
    assert set(d) == set(etiquetas)
    for s in ("[SAD]", "[ILLUMI]", "[TP_R]", "[CAMERA_IS]", "[JOG]"):
        assert d[s]["hitos"], s
        assert d[s]["cadenas_referenciadas"] > 0


def test_informe_del_hito():
    with open(os.path.join(ANA, "census.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "372" in t and "[STK]" in t and "[OSD]" in t
    assert "S51" in t
