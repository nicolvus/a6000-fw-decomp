"""G2 — `string_english.uxc`: ida y vuelta byte a byte, edición y cadena de la tabla de menú (G4)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import uxc_strings

APP = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
STR = APP / "share/app/string_english.uxc"
VIEW2 = APP / "lib/viewUnified2.so"
pytestmark = pytest.mark.skipif(not STR.exists(), reason="firmware 3.21 extraído no disponible")


def test_roundtrip_exacto():
    d = STR.read_bytes()
    head, _, recs = uxc_strings.parse(d)
    assert len(recs) == 4360 and uxc_strings.build(head, recs) == d


def test_edicion_cambia_longitud_y_reindexa():
    head, _, recs = uxc_strings.parse(STR.read_bytes())
    recs[0xE001] = "Extra fine, edited and much longer than before"
    _, _, recs2 = uxc_strings.parse(uxc_strings.build(head, recs))
    assert recs2 == recs


@pytest.mark.skipif(not VIEW2.exists(), reason="viewUnified2.so no disponible")
def test_tabla_creative_style_apunta_a_cadenas_reales():
    # DAT_004cc938 (Ghidra, base +0x10000) = 0x4bc938 vaddr; 0x28 B por ítem: +8 id, +0xc texto, +0x14 ayuda.
    _, _, recs = uxc_strings.parse(STR.read_bytes())
    d = VIEW2.read_bytes()
    w = struct.unpack_from("<10I", d, 0x4B4938 + 0x28)
    assert (w[2], recs[w[3] & 0xFFFF]) == (0x13, "Standard")
    assert recs[w[5] & 0xFFFF].startswith("Standard style")


@pytest.mark.skipif(not VIEW2.exists(), reason="viewUnified2.so no disponible")
def test_busqueda_encuentra_creative_style():
    sys.path.insert(0, str(ROOT / "scripts/gui"))
    import menu_tables

    _, _, recs = uxc_strings.parse(STR.read_bytes())
    found = dict(menu_tables.runs(VIEW2.read_bytes(), recs))
    assert found[0x4B4640] >= 13  # 0x4cc640 en Ghidra (+0x10000) → 0x4bc640 vaddr → 0x4b4640 fichero


A6000_CAUTION = APP / "lib/CautionConfig.so"


@pytest.mark.skipif(not A6000_CAUTION.exists(), reason="CautionConfig.so no disponible")
def test_nodo_silentshutter_a6000_es_steadyshot_y_efcs_tiene_processid():
    sys.path.insert(0, str(ROOT / "scripts/gui"))
    import setting_nodes

    _, _, recs = uxc_strings.parse(STR.read_bytes())
    nodes = dict(setting_nodes.property_lists(A6000_CAUTION, r"^(SilentShutterRoot|CustomFrontCurtainShutterRoot)$"))
    silent = {p: v for p, _, v in nodes["SilentShutterRoot"]}
    assert silent[0xE] == 0x26 and "SteadyShot" in recs[silent[0] & 0xFFFF]
    assert {p: v for p, _, v in nodes["CustomFrontCurtainShutterRoot"]}[0xE] == 0x46


VIEW2_SO = APP / "lib/viewUnified2.so"


@pytest.mark.skipif(not VIEW2_SO.exists(), reason="viewUnified2.so no disponible")
def test_parche_de_paginas_inserta_y_reubica():
    sys.path.insert(0, str(ROOT / "scripts/gui"))
    import add_menu_entry as am

    d = VIEW2_SO.read_bytes()
    out = am.patch(d, 0xEB0)
    segs = am._segments(out)
    assert len(segs) == 6 and segs[-1][0] == 1 and segs[-1][6] == 6  # PT_LOAD RW añadido
    for arr, cnt, movs, lit, add, anchor in am.PAGES:
        assert struct.unpack_from("<H", out, movs)[0] == 0x2200 | (cnt + 1)
        new = (add + 4 + struct.unpack_from("<I", out, lit)[0]) & 0xFFFFFFFF
        o = am._off(segs, new)
        slots = struct.unpack_from(f"<{cnt + 1}I", out, o)
        assert slots[anchor] == 0xEB0  # addendum al símbolo de referencia
        old = struct.unpack_from(f"<{cnt}I", d, am._off(am._segments(d), arr))
        assert list(slots[:anchor]) + list(slots[anchor + 1:]) == list(old)


def test_paquete_silent_menu_semantica_efcs(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts/gui"))
    import build_silent_menu_test as bs
    import setting_nodes

    dev = APP.parent
    a6300 = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
    if not a6300.exists():
        pytest.skip("firmware A6300 no disponible")
    bs.main(dev, a6300, tmp_path)
    vals = {n: {p: v for p, _, v in props} for n, props in setting_nodes.property_lists(tmp_path / "lib/CautionConfig.so", r"^SilentShutter")}
    assert vals["SilentShutterRoot"][0xE] == 0x46  # mismo ProcessId que el menú EFCS
    assert (vals["SilentShutterOff"][0xF], vals["SilentShutterOn"][0xF]) == (0, 1)  # Off = EFCS (0), On = electrónico (1)
    _, _, recs = uxc_strings.parse((tmp_path / "share/app/string_english.uxc").read_bytes())
    label = vals["SilentShutterRoot"][0] & 0xFFFF
    assert recs[label].endswith("Silent Shooting")
    # 3.39: ids de la A6300 (0xf840…) fuera del índice del A6000 (5 958 ranuras) → assert de ResourceManager y pantalla negra
    count = struct.unpack_from("<I", (tmp_path / "share/app/string_english.uxc").read_bytes(), 12)[0] & 0x1FFF
    ids = [v & 0xFFFF for n in vals for p, v in vals[n].items() if p in (0, 6)]
    assert all(i - 0xE000 < count for i in ids), [hex(i) for i in ids]
    # 3.53: sin 0xb/0xc el menú muestra la entrada pero no abre el selector; mismos valores que el nodo EFCS (CustomFrontCurtainShutter)
    assert (vals["SilentShutterRoot"][0xB], vals["SilentShutterRoot"][0xC]) == (2, 0)
    assert all((vals[n][0xB], vals[n][0xC]) == (0, 1) for n in ("SilentShutterOn", "SilentShutterOff"))
    lists = dict(setting_nodes.property_lists(tmp_path / "lib/CautionConfig.so", r"^SilentShutter"))
    assert all([p for p, _, _ in t] == sorted(p for p, _, _ in t) for t in lists.values())  # _getPropertyIndex: búsqueda binaria
    d = (tmp_path / "lib/CautionConfig.so").read_bytes()
    assert [struct.unpack_from("<H", d, a)[0] for a in bs.COUNT_MOVS.values()] == [0x2200 | len(lists[n]) for n in bs.COUNT_MOVS]


def test_build_rechaza_id_fuera_del_indice():
    head, _, recs = uxc_strings.parse((APP / "share/app/string_english.uxc").read_bytes())
    with pytest.raises(AssertionError):
        uxc_strings.build(head, {**recs, 0xF840: "x"})
