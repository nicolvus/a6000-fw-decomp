"""ORDEN.md: las reglas de orden del repositorio se comprueban, no se confían."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

import check_order  # noqa: E402


def test_orden_del_repositorio():
    fallos = check_order.chequeos()
    assert not fallos, "Incumplimientos de ORDEN.md:\n" + "\n".join(f"  - {f}" for f in fallos)


def test_la_numeracion_de_secciones_se_comprueba():
    assert check_order.fallos_numeracion("## 1. a\n## 2. b\n") == []
    assert check_order.fallos_numeracion("## 1. a\n## 1. b\n")   # repetida
    assert check_order.fallos_numeracion("## 1. a\n## 3. b\n")   # salto
