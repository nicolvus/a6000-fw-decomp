"""Tests de S174 — el API de mensajes «…ForLiro» del `libObj.so` (capa camera-user).

Tests de **bytes reales**: si cambia una cadena, un conteo o una lista, fallan.
"""
import json
import os
import re

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = {
    "A6000": os.path.join(ROOT, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/"
                              "dev/nflasha15_unpacked_unpacked/lib/libObj.so"),
    "A7S": os.path.join(ROOT, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/"
                            "dev/nflasha15_unpacked_unpacked/lib/libObj.so"),
    "A6300": os.path.join(ROOT, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/"
                             "dev/nflasha15_unpacked_unpacked/lib/libObj.so"),
}
ANA = os.path.join(ROOT, "analysis/s174_forliro_api")


def _read(path):
    with open(path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def libs():
    return {k: _read(p) for k, p in LIB.items()}


def _forliro(blob):
    return sorted({m.group().decode() for m in re.finditer(rb"[A-Za-z0-9_]{2,40}ForLiro", blob)})


def _soportados(blob):
    return {m.group(1).decode()
            for m in re.finditer(rb"(?<!NON )([A-Za-z0-9_]{2,40}) SUPPORTED MsgID", blob)}


def _rechazados(blob):
    return {m.group(1).decode()
            for m in re.finditer(rb"([A-Za-z0-9_]{2,40}) NON SUPPORTED MsgID", blob)}


# --------------------------------------------------------------------------
# 1) Recuentos
# --------------------------------------------------------------------------

def test_recuento_de_nombres_forliro(libs):
    assert len(_forliro(libs["A6000"])) == 216
    assert len(_forliro(libs["A7S"])) == 221
    assert len(_forliro(libs["A6300"])) == 240


def test_la_a6000_y_la_a7s_no_soportan_ningun_mensaje_forliro(libs):
    for k in ("A6000", "A7S"):
        nombres = set(_forliro(libs[k]))
        assert len(nombres & _soportados(libs[k])) == 0
        assert len(nombres & _rechazados(libs[k])) == len(nombres)


def test_el_a6300_soporta_seis_mensajes_forliro(libs):
    nombres = set(_forliro(libs["A6300"]))
    sup = nombres & _soportados(libs["A6300"])
    assert sup == {"SetApertureSTFForLiro", "SetAutoDualRecModeForLiro",
                   "SetExpandFocusAfModeForLiro", "SetMountAdapterFocusTypeForLiro",
                   "SetPowerStatusForLiro", "SetVolpfModeForLiro"}
    # ninguno de los 6 es del obturador
    assert not any(x.startswith(("SetShut", "SetSilent", "SetFront", "SetIris", "SetDrive"))
                   for x in sup)


def test_conteos_de_los_mensajes_de_soporte_y_rechazo(libs):
    assert libs["A6000"].count(b"NON SUPPORTED MsgID") == 222
    assert libs["A7S"].count(b"NON SUPPORTED MsgID") == 227
    assert libs["A6300"].count(b"NON SUPPORTED MsgID") == 241
    for k in ("A6000", "A7S"):
        assert len(_soportados(libs[k])) == 1   # solo el 'NONE SUPPORTED' mal partido
    assert len(_soportados(libs["A6300"])) == 7


# --------------------------------------------------------------------------
# 2) La familia del obturador
# --------------------------------------------------------------------------

@pytest.mark.parametrize("nombre", [
    "SetShutDriveForLiro", "SetShutDriveModeForLiro", "SetShutLowLimitForLiro",
    "SetSilentShutterModeForLiro", "SetFrontEShutterModeForLiro", "SetIrisDriveForLiro",
    "SetDriveModeForLiro", "SetMovieAutoSlowshutModeForLiro",
])
def test_la_familia_del_obturador_esta_en_los_tres_pero_rechazada(libs, nombre):
    for k in ("A6000", "A7S", "A6300"):
        nombres = set(_forliro(libs[k]))
        assert nombre in nombres, (k, nombre)
        assert nombre in _rechazados(libs[k]), (k, nombre)
        assert nombre not in _soportados(libs[k]), (k, nombre)


def test_set_shutter_type_for_liro_solo_en_el_a6300(libs):
    assert "SetShutterTypeForLiro" not in _forliro(libs["A6000"])
    assert "SetShutterTypeForLiro" not in _forliro(libs["A7S"])
    assert "SetShutterTypeForLiro" in _forliro(libs["A6300"])


def test_la_prueba_de_soporte_es_exacta_no_por_proximidad(libs):
    """El nombre debe ir seguido literalmente de ' NON SUPPORTED MsgID'."""
    b = libs["A6000"]
    i = b.find(b"SetShutDriveForLiro")
    assert i > 0
    assert b[i + len(b"SetShutDriveForLiro"):i + len(b"SetShutDriveForLiro") + 20].startswith(
        b" NON SUPPORTED MsgID")


# --------------------------------------------------------------------------
# 3) Diferenciales de nombres
# --------------------------------------------------------------------------

def test_diferencial_de_nombres(libs):
    a6 = set(_forliro(libs["A6000"]))
    a7 = set(_forliro(libs["A7S"]))
    ac = set(_forliro(libs["A6300"]))
    assert len(ac - a6) == 25
    assert (a6 - ac) == {"SetStepzoomModeForLiro"}
    assert len(a7 - a6) == 5
    assert "SetShutterTypeForLiro" in (ac - a6)
    assert "SetSteadyShotAdvancedStillForLiro" in (ac - a6)


# --------------------------------------------------------------------------
# 4) Datos estructurados
# --------------------------------------------------------------------------

def test_json_del_hito_consistente():
    with open(os.path.join(ANA, "forliro_api.json"), encoding="utf-8") as fh:
        j = json.load(fh)
    assert j["milestone"] == "S174"
    f = j["firmwares"]
    assert len(f["A6000_fw321"]["nombres_forliro"]) == 216
    assert len(f["A7S_fw320"]["nombres_forliro"]) == 221
    assert len(f["A6300_fw201"]["nombres_forliro"]) == 240
    assert f["A6000_fw321"]["forliro_soportados"] == []
    assert f["A7S_fw320"]["forliro_soportados"] == []
    assert len(f["A6300_fw201"]["forliro_soportados"]) == 6
    assert len(j["solo_en_a6300"]) == 25
    assert j["solo_en_a6000"] == ["SetStepzoomModeForLiro"]
    assert "A=NO, B=NO, C=NO" in j["efecto_en_S51"]
    assert "NO prueba una funcionalidad" in j["regla_metodologica"]


def test_informe_del_hito():
    with open(os.path.join(ANA, "forliro_api.md"), encoding="utf-8") as fh:
        t = fh.read()
    assert "SetShutterTypeForLiro" in t
    assert "NON SUPPORTED" in t and "SUPPORTED MsgID" in t
    assert "S51" in t
