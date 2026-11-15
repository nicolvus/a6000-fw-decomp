import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import live


def test_im_elf_caido_es_arranque_fallido_de_inmediato():
    assert live.arranque_fallido("LIVE=/dev/vport0p1\nIMEXIT im_s 139\n", 40, 0, 240)


def test_sin_pantalla_pasado_el_limite_es_arranque_fallido():
    assert live.arranque_fallido("LIVE=/dev/vport0p1\n", 241, 0, 240)
    assert not live.arranque_fallido("LIVE=/dev/vport0p1\n", 200, 0, 240)


def test_con_pantalla_nunca_es_fallido():
    assert not live.arranque_fallido("LIVE=/dev/vport0p1\n", 900, 3, 240)
    assert not live.arranque_fallido("IMEXIT im_s 0\n", 900, 3, 240)
