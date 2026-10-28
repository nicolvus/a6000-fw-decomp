"""E25-19b: hechos de la compuerta de eventos (0x43afc544) comprobados por bytes de av-cam.bin."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from e25_19b_callers import callers
from e25_19b_dis import BIN, dis

pytestmark = pytest.mark.skipif(not BIN.exists(), reason="falta av-cam.bin")


def first(addr: int) -> str:
    return dis(BIN.read_bytes(), addr, 4)[0].split(": ", 1)[1]


def test_campos_de_la_compuerta():
    assert first(0x43AFC15A) == "ldrb.w r0, [r0, #0x24]"  # bloqueado
    assert first(0x43AFBF44) == "ldr r0, [r0, #0x1c]"  # id de grupo de M
    assert first(0x43AE75DC) == "ldr r0, [r0]"  # cap = [M]
    d = "\n".join(dis(BIN.read_bytes(), 0x43AFC160, 0x10))
    assert "[r0, #0x2d]" in d and "[r0, #0x2c]" in d and "movhs r0, #0" in d  # en_vuelo < max


def test_bloqueo_de_grupo_solo_desde_un_sitio():
    c = callers(BIN.read_bytes(), {0x437E52B0, 0x437E54B4})
    assert c[0x437E52B0] == [0x437DE594] and c[0x437E54B4] == [0x437DE134]
