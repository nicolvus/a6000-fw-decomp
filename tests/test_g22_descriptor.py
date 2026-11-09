"""G22: descriptor de Silent en `cmn_view_processDataMgr.so` (ProcessId 0x12) — estructura y relocaciones (offline)."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import silent_descriptor as S

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/cmn_view_processDataMgr.so"
needs = pytest.mark.skipif(not LIB.is_file(), reason="cmn_view_processDataMgr.so de Sony ausente")


def _rd(d, segs, va, n):
    return struct.unpack_from(f"<{n}I", d, A._off(segs, va))


@needs
def test_descriptor_de_silent_clona_efcs_con_los_numeros_de_la_a7s():
    old = LIB.read_bytes()
    new = S.patch(old)
    segs = A._segments(new)
    dv = _rd(new, segs, S.TABLA_D + 4 * S.PID_NUEVO, 1)[0]
    desc = _rd(new, segs, dv, S.DESC_PALABRAS)
    ref = _rd(old, A._segments(old), S.DESC_EFCS, S.DESC_PALABRAS)
    assert [w for i, w in enumerate(desc) if i != 6] == [w for i, w in enumerate(ref) if i != 6]
    model = _rd(new, segs, desc[6], S.MODEL_PALABRAS)
    assert model[1:4] == (1, 0x5B, 0x6C) and model[8] == 0x201
    assert _rd(new, segs, model[4], 1)[0] == 0x291 and _rd(new, segs, model[5], 1)[0] == 0x292
    ref_model = _rd(old, A._segments(old), ref[6], S.MODEL_PALABRAS)
    assert model[0] == ref_model[0] and model[6:] == ref_model[6:]      # mismo "@M00F", listas S2/S3 compartidas
    assert _rd(new, segs, S.TABLA_D + 4 * S.PID_EFCS, 1)[0] == S.DESC_EFCS  # EFCS intacto


@needs
def test_reloca_cada_puntero_copiado():
    old, new = LIB.read_bytes(), S.patch(LIB.read_bytes())

    def rels(d):
        segs = A._segments(d)
        _, dyn = A._dynamic(d, segs)
        t = {k: v for k, v in dyn if k}
        o = A._off(segs, t[0x11])
        return {struct.unpack_from("<I", d, o + i)[0] for i in range(0, t[0x12], 8)}

    añadidas = rels(new) - rels(old)
    assert len(añadidas) >= 8 and all(a >= 0xA0000 for a in añadidas)
