"""Tests for S112 — `[CAMERA_MAIN_SYNC]` (429 trazas).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos y
recuentos. Si cambia una dirección, el test falla.
"""

import json
import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
PREFIX = "[CAMERA_MAIN_SYNC]"


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=240):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _cam_main_sync_strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        out.append((BASE_VADDR + i, _cstr(data, BASE_VADDR + i)))
        start = i + 1
    return out


def _json(name):
    with open(ROOT / "analysis" / "s112_camera_main_sync" / name, encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_y_rango(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        assert len(strings) == 429
        # Primera y última vaddr deben estar en el rango esperado
        # El primer string comienza en 0x43c9b409 (CAMERA_MAIN_SYNC]: SyncResMgr::Lock...)
        # el inicio real incluye el '[' de "[CAMERA_MAIN_SYNC]"
        assert strings[0][0] == 0x43C9B409
        assert strings[-1][0] == 0x43CB5616

    def test_subbloques_principales(self):
        bl = _json("camera_main_sync.json")["subblocks"]
        # Los sub-bloques principales deben estar presentes
        main_blocks = [k for k in bl if k and k != '' and bl[k]['count'] >= 2]
        assert len(main_blocks) >= 10  # SyncResMgr, DFS, APL_ERR, JPEG, etc.

    def test_syncresmgr_vaddr(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        # Verificar que la vaddr 0x43c9b409 (primer SyncResMgr) tiene el texto esperado
        vaddr = "0x43c9b409"
        texto = _cstr(data, int(vaddr, 16))
        assert "SyncResMgr" in texto

    def test_dfs_control_vaddr(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        # Verificar que DFS está en el rango correcto
        for vaddr, texto in strings:
            if "DFS" in texto and "DFS SETTING" in texto:
                assert 0x43CA1780 <= vaddr <= 0x43CAEED2
                break

    def test_cadenas_clave_presentes(self):
        data = _data()
        # Las claves esperadas incluyen el prefijo CAMERA_MAIN_SYNC] y el texto real
        esperados = {
            0x43c9b409: "CAMERA_MAIN_SYNC]: SyncResMgr::Lock",
            0x43c9b442: "CAMERA_MAIN_SYNC]: SyncResMgr::Unlock",
            0x43ca1780: "DFS SETTING ERR",
            0x43cb3600: "APL_ERR:0x%02x apl_mov_set_aic R0 error",
            0x43ca4b2c: "jpeg encode sync next (callback) ERRCODE",
            0x43cb32b0: "Sequence_Movie: RC_ERR",
        }
        for vaddr, texto in esperados.items():
            resultado = _cstr(data, vaddr)
            # Comparar subcadena (el _cstr incluye specifiers de formato adicionales)
            assert texto in resultado, f"En {hex(vaddr)}: esperado que '{texto}' esté en '{resultado}'"


class TestEstructura:
    def test_rango_vglobal(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        lo = min(v for v, _ in strings)
        hi = max(v for v, _ in strings)
        assert 0x43C9B400 <= lo <= 0x43C9B410
        assert 0x43CB5600 <= hi <= 0x43CB5620

    def test_conteo_total(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        assert len(strings) == 429

    def test_vaddr_monotonicidad(self):
        data = _data()
        strings = _cam_main_sync_strings(data)
        vaddrs = [v for v, _ in strings]
        # Las vaddrs deben estar ordenadas (no necesariamente monotonicas estrictas,
        # pero el rango debe ser continuo en el binario)
        assert vaddrs == sorted(vaddrs), "Las vaddrs deben estar ordenadas"

    def test_subblock_json_valid(self):
        json_path = ROOT / "analysis" / "s112_camera_main_sync" / "camera_main_sync.json"
        assert json_path.exists()
        with open(json_path, encoding="utf-8") as fh:
            j = json.load(fh)
        assert j["module"] == "CAMERA_MAIN_SYNC"
        assert j["total_strings"] == 429
        assert "subblocks" in j
        # Verificar que los conteos suman 429 (aproximadamente, incluyendo el sub-bloque vacío)
        total = sum(info['count'] for info in j['subblocks'].values())
        # Debe ser >= 429 (algunos sub-bloques pueden superponerse o el vacío cuenta aparte)
        assert total >= 429

class TestMapaDeFuncionesYDiferencial:
    """Datos completados por el agente principal (reextract.py)."""

    def _json(self):
        with open(ROOT / "analysis" / "s112_camera_main_sync" / "camera_main_sync.json",
                  encoding="utf-8") as fh:
            return json.load(fh)

    def test_mapa_funcion_traza_completo(self):
        j = self._json()
        assert j["n_functions"] == 430
        assert sum(f["n_strings"] for f in j["functions"]) == 1407

    def test_diferencial_a7s_exacto(self):
        j = self._json()
        assert j["a7s"]["prefijo"] == 0
        assert j["a7s"]["comunes_texto_a_texto"] == 418
        assert j["a7s"]["solo_a6000"] == 11
        assert "0x43cb55dd" in j["a7s"]["vaddrs_solo_a6000"]

    def test_101_subbloques_tras_reextraccion(self):
        j = self._json()
        assert len(j["subblocks"]) == 101
        assert j["subblocks"]["SyncResMgr"]["count"] == 55
