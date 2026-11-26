"""ORDEN.md: las reglas de orden del repositorio se comprueban, no se confían."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "audit"))

import check_order  # noqa: E402


def test_orden_del_repositorio():
    fallos = check_order.chequeos()
    assert not fallos, "Incumplimientos de ORDEN.md:\n" + "\n".join(f"  - {f}" for f in fallos)
