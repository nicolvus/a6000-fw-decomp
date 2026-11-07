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
