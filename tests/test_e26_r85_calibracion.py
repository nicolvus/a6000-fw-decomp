"""E26-R85: tabla EFCS desde fotos (puntos medidos) y r5 del modo silencioso calibrado (R56 §7)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/e26_r76")]

import camera_silent as S  # noqa: E402
import e26_r85_calibrar_fotos as C  # noqa: E402


def test_tabla_efcs_desde_puntos_r85():
    C.selftest()


def test_r5_silencioso_calibrado():
    assert S.r5_for(1 / 60) == 3320 and S.r5_for(1 / 250) == 4077      # valores medidos en R56 §7
    assert S.r5_for(1 / 3000) == S.R5_FULL - 1                           # acotado: el modelo da ≤ 0 filas
    assert S.r5_for(1 / 10) == -1                                        # más largo que un cuadro
