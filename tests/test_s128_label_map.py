"""Tests for S128 — el mapa de etiquetado de la fw3.21 (A6000 vs A7S)."""

import json
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
A6000 = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PAT = re.compile(rb"[\x20-\x7e]{4,}")


def _data(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _map():
    with open(ROOT / "analysis" / "s128_label_map" / "label_map.json", encoding="utf-8") as fh:
        return json.load(fh)


def _por_prefijo(data):
    out = {}
    for m in PAT.finditer(data):
        t = m.group().decode("latin1")
        mm = re.match(r"\[([A-Z][A-Z0-9_]{1,24})\]", t)
        if mm:
            out.setdefault(mm.group(1), []).append(t)
    return out


class TestMapa:
    def test_cifras_globales(self):
        m = _map()
        assert m["counts"]["IGUAL"] == 58
        assert m["counts"]["RENOMBRADO"] == 18
        assert m["counts"]["PARCIAL"] == 2
        assert m["counts"]["NUEVO/PROPIO"] == 20
        assert len(m["modulos"]) == 98

    def test_modulos_renombrados_de_la_fw321(self):
        m = _map()
        por = {r["prefijo"]: r for r in m["modulos"]}
        for pref, n in (("CAMERA_MAIN_YC", 958), ("IMAGING_CAP", 678),
                        ("CAMERA_MAIN_SYNC", 412), ("CAMERA_SA", 228),
                        ("CAMERA_MAIN_TC", 122), ("IMAGING", 115)):
            r = por[pref]
            assert r["clase"] == "RENOMBRADO", pref
            assert r["usa_prefijo_en_a7s"] == 0, pref
            assert r["comunes_sin_prefijo"] == n, pref

    def test_cam_imager_es_el_unico_cambio_de_contenido_grande(self):
        m = _map()
        por = {r["prefijo"]: r for r in m["modulos"]}
        assert por["CAM_IMAGER"]["clase"] == "PARCIAL"
        assert por["CAM_IMAGER"]["n_a6000"] == 371
        assert por["CAM_IMAGER"]["comunes_sin_prefijo"] == 179

    def test_modulos_identicos_usan_el_prefijo_en_la_a7s(self):
        m = _map()
        por = {r["prefijo"]: r for r in m["modulos"]}
        for pref in ("ADF", "SDF", "IDT", "CDIAG", "TRK", "SFRS", "SFRA"):
            assert por[pref]["clase"] == "IGUAL", pref
            assert por[pref]["usa_prefijo_en_a7s"] > 0, pref


class TestBytes:
    def test_los_18_renombrados_no_existen_como_prefijo_en_la_a7s(self):
        a7s = _data(A7S)
        m = _map()
        for r in m["modulos"]:
            if r["clase"] == "RENOMBRADO":
                assert ("[" + r["prefijo"] + "]").encode() not in a7s, r["prefijo"]

    def test_los_textos_sin_etiqueta_son_los_mismos(self):
        a6000 = _data(A6000)
        a7s = _data(A7S)
        pref = "IMAGING_CAP"
        textos = [m.group().decode("latin1") for m in PAT.finditer(a6000)
                  if m.group().startswith(b"[IMAGING_CAP]")]
        assert len(textos) == 697
        runs7s = {m.group().decode("latin1") for m in PAT.finditer(a7s)}
        comunes = sum(1 for t in textos if t[len(pref) + 4:] in runs7s)
        assert comunes == 678
