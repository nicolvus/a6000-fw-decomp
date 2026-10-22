"""Tests for S131 — `[VPH_API]`, la API de parámetros del subsistema VPH (106 trazas)."""

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PAT = re.compile(rb"\[VPH_API\][\x20-\x7e]*")


def _data(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _res():
    with open(ROOT / "analysis" / "s131_vph_api" / "vph_api.json", encoding="utf-8") as fh:
        return json.load(fh)


def _cadenas(data):
    return [(m.group().decode("latin1")) for m in PAT.finditer(data)]


class TestInventario:
    def test_cifras_y_rango(self):
        data = _data(A6000)
        r = _res()
        assert r["counts"]["cadenas"] == 106
        assert len(_cadenas(data)) == 106
        assert r["rango"] == ["0x43ce32e7", "0x43ce3dfc"]
        assert r["counts"]["entrada"] == 49
        assert r["counts"]["entrada_sub"] == 42
        assert r["counts"]["salida"] == 11
        assert r["counts"]["otro"] == 4
        assert r["counts"]["familias"] == 60

    def test_cadenas_clave_en_su_direccion(self):
        data = _data(A6000)
        base = 0x43541000
        esperados = {
            0x43CE32E7: "[VPH_API]<mode>",
            0x43CE3634: "[VPH_API]<shutter_mute_param>",
            0x43CE3B5A: "[VPH_API]<shutter_mute_param_sub>",
            0x43CE3DE4: "[VPH_API]>shutter_mute<",
            0x43CE3DFC: "[VPH_API]>shutter_mute_status<o/f:%d",
            0x43CE3D0E: "[VPH_API]>mode_status<",
            0x43CE374B: "[VPH_API]=v_command_comp=",
        }
        for va, texto in esperados.items():
            off = va - base
            assert data[off:off + len(texto)] == texto.encode(), hex(va)

    def test_los_manejadores_forman_dos_bloques(self):
        r = _res()
        addrs = sorted(int(k, 16) for k in r["funciones"])
        assert len(addrs) == 48
        assert addrs[0] == 0x4395AAB8
        assert addrs[-1] == 0x4395E34C
        # dos bloques: 0x4395aab8-0x4395b5f4 y 0x4395e1b8-0x4395e34c
        bloque_a = [a for a in addrs if a <= 0x4395B5F4]
        bloque_b = [a for a in addrs if a >= 0x4395E1B8]
        assert len(bloque_a) == 39
        assert len(bloque_b) == 9
        for grupo in (bloque_a, bloque_b):
            for a, b in zip(grupo, grupo[1:]):
                assert 0 < b - a <= 160, (hex(a), hex(b))


class TestDiferencial:
    def test_la_api_no_existe_en_los_otros_firmwares(self):
        assert _data(A6000).count(b"[VPH_API]") == 106
        assert _data(A7S).count(b"[VPH_API]") == 0
        assert _data(A6300).count(b"[VPH_API]") == 0

    def test_el_token_vph_crece_en_la_a6000(self):
        r = _res()
        assert r["diff"]["a6000_token_vph"] == 134
        assert r["diff"]["a7s_token_vph"] == 24
        assert r["diff"]["a6300_token_vph"] == 24


class TestShutterMute:
    def test_la_api_del_silenciador_es_nueva_en_fw321(self):
        a6000 = _data(A6000)
        a7s = _data(A7S)
        a6300 = _data(A6300)
        assert a6000.count(b"shutter_mute") == 4
        assert a7s.count(b"shutter_mute") == 0
        assert a6300.count(b"shutter_mute") == 0
        # pero la traza del silenciador en si esta en los tres
        for blob in (a6000, a7s, a6300):
            assert b"shutter mute on/off" in blob

    def test_el_silenciador_no_aparece_como_obturador_electronico(self):
        r = _res()
        for nombre, v in r["familias"].items():
            if "shutter" in nombre:
                for texto in (v.get("entrada"), v.get("entrada_sub"), v.get("salida")):
                    if texto:
                        bajo = texto.lower()
                        for palabra in ("electro", "silent", "curtain", "efcs"):
                            assert palabra not in bajo, (nombre, texto)
