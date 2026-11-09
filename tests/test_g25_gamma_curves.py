"""G25: curvas S-Log2 e ITU709(800%) del núcleo (`pp_curves_patch.py`, números de gamma 0x14/0x15, solo datos) + emulación de la selección de gamma (offline)."""
from __future__ import annotations

import importlib.util
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import pp_curves_patch as C
import pp_menu_spec as M

BASE = ROOT / "analysis/rea-independent/input/av-cam.bin"
needs = pytest.mark.skipif(not (BASE.is_file() and C.A7S.is_file()), reason="av-cam de la A6000/A7S ausente")


@needs
def test_curvas_nuevas_en_0x14_y_0x15_con_su_propio_numero():
    base, a7s = BASE.read_bytes(), C.A7S.read_bytes()
    new = C.apply(base, C.patches(base, a7s))
    for g, orig in ((0x14, 0x1C), (0x15, 0x1D)):
        p = struct.unpack_from("<I", new, C.TAB["a6000"] + 8 * g + 4 - C.BASE)[0]
        c = new[p - C.BASE:p - C.BASE + C.CURVE]
        ref = a7s[struct.unpack_from("<I", a7s, C.TAB["a7s"] + 8 * orig + 4 - C.BASE)[0] - C.BASE:][:C.CURVE]
        assert c[0x1014] == g and c[0x1012] == 4 and c[:0x1012] == ref[:0x1012]
        assert struct.unpack_from("<I", base, C.TAB["a6000"] + 8 * g + 4 - C.BASE)[0] == 0         # estaban vacías en la A6000
    assert [list(new[C.SEL["a6000"] - C.BASE + 2 * i:][:2]) for i in (10, 11)] == [[0x14, 0x14], [0x15, 0x15]]


@needs
def test_la_seleccion_de_gamma_emulada_da_0x14_y_0x15_y_no_cambia_lo_demas():
    spec = importlib.util.spec_from_file_location("emu", ROOT / "analysis/gui/g18/emu_gamma.py")
    emu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(emu)
    base, a7s = BASE.read_bytes(), C.A7S.read_bytes()
    new = C.apply(base, C.patches(base, a7s))
    got = {s: emu.run(new, s)["bd9"] for s in (0, 3, 4, 5, 6, 7, 8, 9, 10, 11)}
    assert got == {0: 10, 3: 0x16, 4: 10, 5: 0, 6: 0x18, 7: 0x19, 8: 0x1A, 9: 0x1B, 10: 0x14, 11: 0x15}


def test_menu_gamma_completo_sigue_el_orden_de_la_a6300():
    assert [t for t, _ in M.GAMMA_COMPLETA] == ["Movie", "Still", "Cine1", "Cine2", "Cine3", "Cine4", "ITU709", "ITU709(800%)", "S-Log2"]
    assert dict(M.GAMMA_COMPLETA)["ITU709(800%)"] == 10 and dict(M.GAMMA_COMPLETA)["S-Log2"] == 11
