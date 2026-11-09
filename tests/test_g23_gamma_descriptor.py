"""G23: descriptor de Gamma PP en `cmn_view_processDataMgr.so` (ProcessId 0x3c) — estructura y relocaciones (offline)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import pp_gamma_descriptor as G

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/cmn_view_processDataMgr.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="cmn_view_processDataMgr.so de Sony ausente")


def _rd(d, va, n=1):
    return struct.unpack_from(f"<{n}I", d, A._off(A._segments(d), va))


@needs
def test_gamma_escribe_0x214_lee_0x216_con_siete_opciones():
    new = G.patch(LIB.read_bytes())
    desc = _rd(new, _rd(new, G.TABLA_D + 4 * G.PID)[0], G.DESC_PALABRAS)
    assert desc[5] >> 8 & 0xFF == len(G.GAMMAS) == 7
    model = _rd(new, desc[6], G.MODEL_PALABRAS)
    assert model[1:4] == (1, 0x40, 0x49) and model[8] == 0x701
    assert _rd(new, model[4])[0] == 0x214 and _rd(new, model[5])[0] == 0x216 and _rd(new, model[6])[0] == 1
    assert _rd(new, model[7], 7) == (4, 5, 3, 6, 7, 8, 9)
    assert _rd(new, desc[1], 7) == (0xA45,) * 7
    assert _rd(new, model[0], 6) and new[A._off(A._segments(new), model[0]):][:6] == b"@M00B\0"


@needs
def test_no_toca_otros_pids_ni_el_0x12():
    old = LIB.read_bytes()
    new = G.patch(old)
    for pid in (0x12, 0x3F, 0x46):
        assert _rd(new, G.TABLA_D + 4 * pid)[0] == _rd(old, G.TABLA_D + 4 * pid)[0]


@needs
def test_reloca_cada_puntero_nuevo():
    def rels(d):
        segs = A._segments(d)
        _, dyn = A._dynamic(d, segs)
        t = {k: v for k, v in dyn if k}
        o = A._off(segs, t[0x11])
        return {struct.unpack_from("<I", d, o + i)[0] for i in range(0, t[0x12], 8)}

    old = LIB.read_bytes()
    añadidas = rels(G.patch(old)) - rels(old)
    assert len(añadidas) == 7 and all(a >= 0xA0000 for a in añadidas)
