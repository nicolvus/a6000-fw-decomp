"""E26-R56: pkt[0x0e] = ajuste EFCS en vivo, en línea dentro de 0x438d0064 (sin cuevas, bloque TPZL 0 intacto)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e25_24 import emu
from e25_24 import patch_bionz as PB
from e26_r56 import patch_send_inline as PI

capstone = pytest.importorskip("capstone")
pytest.importorskip("unicorn")
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
needs = pytest.mark.skipif(not AVCAM.is_file(), reason="av-cam.bin original ausente")


@pytest.fixture(scope="module")
def pair() -> tuple[bytes, bytes]:
    orig = AVCAM.read_bytes()
    assert hashlib.sha256(orig).hexdigest() == PB.SHA256
    return orig, PI.apply_bytes(orig)[0]


@needs
def test_solo_cambia_el_tramo_y_revierte(pair):
    orig, out = pair
    diff = [i for i, (a, b) in enumerate(zip(orig, out)) if a != b]
    assert diff and all(PI.SITE - PB.BASE <= i < PI.SITE - PB.BASE + len(PI.OLD) for i in diff)
    assert PI.restore_bytes(out) == orig


@needs
def test_no_toca_la_cabecera_ni_las_cuevas(pair):
    orig, out = pair
    # bloque TPZL 0 de nflasha3 = principio de av-cam (cabecera y zona 0x43541800): debe quedar como Sony
    assert out[:0x1000] == orig[:0x1000]


@needs
def test_desensamblado(pair):
    _, out = pair
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    code = out[PI.SITE - PB.BASE:PI.SITE - PB.BASE + 6]
    text = [(i.mnemonic, i.op_str) for i in md.disasm(code, PI.SITE)]
    assert text == [("ldr", "r3, [pc, #8]"), ("ldr", "r3, [r3]"), ("b", "#0x438d01c2")]
    lit = PI.SITE + 10
    assert int.from_bytes(out[lit - PB.BASE:lit - PB.BASE + 4], "little") == PI.LIVE_EFCS


@needs
@pytest.mark.parametrize("live", [0, 1])
def test_emulacion_envio(pair, live):
    """Desde 0x438d01ae hasta el strb de 0x438d01fa: pkt[0x0e] = ajuste en vivo."""
    _, out = pair
    assert emu.run_bionz_send_from(out, PI.SITE, live) == live
