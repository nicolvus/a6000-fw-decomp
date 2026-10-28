"""E25-19f: la rama c38==0 de EndExps no alcanza el store 0x4354b0ac."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/e25_19f"))
from cfg_alcance import alcanza


def test_rama_b_no_alcanza_store() -> None:
    assert alcanza(0x4354B23A, 0x4354B0AC) is None
    assert alcanza(0x4354B23A, 0x4354AEA4) is None


def test_rama_a_alcanza_store() -> None:
    assert alcanza(0x4354A678, 0x4354B0AC) is not None
