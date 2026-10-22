"""Tests for S130 — los 20 módulos "NUEVO/PROPIO" del mapa de etiquetado (S128)."""

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
PAT = re.compile(rb"[\x20-\x7e]{4,}")


def _data(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _res():
    with open(ROOT / "analysis" / "s130_new_modules" / "new_modules.json", encoding="utf-8") as fh:
        return json.load(fh)


def _por_pref(data):
    out = {}
    for m in PAT.finditer(data):
        t = m.group().decode("latin1")
        mm = re.match(r"^\[([A-Z][A-Z0-9_]{1,24})\]", t)
        if mm:
            out.setdefault(mm.group(1), []).append(t)
    return out


def _nucleo(pref, texto):
    i = texto.find("]")
    resto = texto[i + 1:]
    if resto.startswith(":"):
        resto = resto[1:]
    return resto[1:] if resto.startswith(" ") else resto


class TestClasificacion:
    def test_cifras_globales(self):
        r = _res()
        assert r["counts"]["ETIQUETADO"] == 2
        assert r["counts"]["PARCIAL"] == 1
        assert r["counts"]["CONTENIDO NUEVO"] == 17
        assert len(r["modulos"]) == 20

    def test_solo_idt_opd_y_dfe_son_cambio_de_etiqueta(self):
        r = _res()
        por = {m["prefijo"]: m for m in r["modulos"]}
        etiquetados = sorted(m["prefijo"] for m in r["modulos"] if m["clase"] == "ETIQUETADO")
        assert etiquetados == ["DFE", "IDT_OPD"]
        # IDT_OPD: 270 de 273 nucleos en la A7S, todos bajo la etiqueta [IDT]
        assert por["IDT_OPD"]["nucleos_en_a7s"] == 270
        assert por["IDT_OPD"]["etiqueta_en_a7s"]["IDT"] == 270
        # DFE: 11 de 11
        assert por["DFE"]["nucleos_en_a7s"] == 11

    def test_modulos_nuevos_sin_presencia_en_los_otros_firmwares(self):
        r = _res()
        por = {m["prefijo"]: m for m in r["modulos"]}
        for pref in ("ACCY", "VPH_API", "CLK_CTRL", "DEPTH", "PANDA",
                     "CAMERA_MAIN_FC", "ADC_DEBUG", "LIF_DEBUG", "JOG"):
            assert por[pref]["nucleos_en_a7s"] == 0, pref
            assert por[pref]["nucleos_en_a6300"] == 0, pref
            assert por[pref]["clase"] == "CONTENIDO NUEVO", pref


class TestBytes:
    def test_los_tokens_de_esos_modulos_no_existen_en_los_otros_firmwares(self):
        a7s = _data(A7S)
        a6300 = _data(A6300)
        for tok in (b"ACCY", b"VPH_API", b"CLK_CTRL", b"CAMERA_MAIN_LC",
                    b"MOUNT_DEBUG", b"ILLUMI", b"PANDA"):
            assert a7s.count(tok) == 0, tok
            assert a6300.count(tok) == 0, tok

    def test_el_nucleo_de_los_nuevos_si_se_busca_directamente(self):
        a6000 = _data(A6000)
        a7s = _data(A7S)
        por = _por_pref(a6000)
        for pref in ("ACCY", "VPH_API", "CLK_CTRL"):
            textos = por[pref]
            assert len(textos) >= 9
            for t in textos:
                nucleo = _nucleo(pref, t)
                if len(nucleo) > 20:
                    assert nucleo.encode("latin1") not in a7s, (pref, nucleo[:40])

    def test_api_nueva_del_silenciador_del_obturador(self):
        a6000 = _data(A6000)
        a7s = _data(A7S)
        a6300 = _data(A6300)
        # las 4 trazas de la API de silenciador (nuevas en fw3.21)
        assert a6000.count(b"shutter_mute") == 4
        assert a7s.count(b"shutter_mute") == 0
        assert a6300.count(b"shutter_mute") == 0
        # pero la traza del silenciador en si esta en los tres
        for blob in (a6000, a7s, a6300):
            assert b"shutter mute on/off" in blob
        for texto in (b"[VPH_API]<shutter_mute_param>",
                      b"[VPH_API]<shutter_mute_param_sub>",
                      b"[VPH_API]>shutter_mute<",
                      b"[VPH_API]>shutter_mute_status<o/f:%d"):
            assert texto in a6000, texto

    def test_idt_opd_sigue_teniendo_su_gemelo_idt(self):
        a6000 = _data(A6000)
        # 274 apariciones del token (273 cadenas que empiezan por el + 1 anidada, S120)
        assert a6000.count(b"[IDT_OPD]") == 274
        cadenas = [t for t in (m.group().decode("latin1") for m in PAT.finditer(a6000))
                   if t.startswith("[IDT_OPD]")]
        assert len(cadenas) == 273
        assert a6000.count(b"[IDT]") >= 297
