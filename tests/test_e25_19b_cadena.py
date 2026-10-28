"""E25-19b: la cadena estática hacia `cap` se deriva de los bytes de av-cam.bin."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import e25_19b_cadena as ch

pytestmark = pytest.mark.skipif(not ch.BIN.exists(), reason="av-cam.bin no disponible")


def test_static_chain():
    c = ch.static_chain(ch.BIN.read_bytes())
    assert (c["slot_matriz"], c["matriz"], c["tabla_selectores"]) == (0x440267BC, 0x43FF8F70, 0x43FF8FB4)
    assert c["gestores"][8] == 0x43EDBDCC and c["gestores"][0] == 0
    assert c["selectores"][8] == 0x437EA035 and len(c["selectores"]) == 16
