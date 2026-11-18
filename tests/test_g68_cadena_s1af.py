"""G75 T53 — cadena estática que alimenta la cueva de DR Prioridad: 0x689520 solo se alcanza por la ruta del mensaje de modelo tipo 0x4e (no por el S1 normal 0x7506)."""
import sys
from pathlib import Path

import capstone
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g61")]
import intervalo_patch as G61

pytestmark = pytest.mark.skipif(not G61.SRC.exists(), reason="sin libObj extraído")


def _ins(lo, hi):
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.skipdata = True
    return list(md.disasm(G61.SRC.read_bytes()[lo:hi], lo))


def _llamadas(destino):
    return [i.address for i in _ins(0x2000, 0x9A0000) if i.mnemonic in ("bl", "b.w") and i.op_str == f"#{destino:#x}"]


def test_cueva_solo_por_mensaje_de_modelo_0x4e():
    assert _llamadas(0x689520) == [0x689676]  # envoltorio 0x689628 (lee el parámetro 0x23e)
    assert _llamadas(0x689628) == [0x68A270]  # caso del despachador por tipo de mensaje
    assert _llamadas(0x689F44) == [0x69AA80]  # thunk virtual 0x69aa78
    d = {i.address: i for i in _ins(0x68A098, 0x68A0A2)}
    assert d[0x68A098].op_str == "r0, #0x4e" and d[0x68A09A].op_str == "#0x68a26c"  # tipo 0x4e -> 0x689628
    assert any(i.op_str == "#0x689628" for i in _ins(0x68A26C, 0x68A274))
