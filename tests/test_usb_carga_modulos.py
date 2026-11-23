import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'scripts' / 'usb_carga'))
import modulos

KO = modulos.KMOD_A6300 / 'usb_darwin.ko'
pytestmark = pytest.mark.skipif(not KO.exists(), reason='firmware A6300 no extraído')


def test_parche_solo_toca_las_cuatro_llamadas_gpio():
    orig = KO.read_bytes()
    nuevo = modulos.parchear(orig)
    sitios = modulos.sitios_gpio(orig)
    assert len(nuevo) == len(orig) and len(sitios) == 4
    tocados = set()
    for ent, ins in sitios:
        assert nuevo[ins:ins + 4] == modulos.NOP
        assert nuevo[ent + 4] == modulos.R_ARM_NONE  # byte bajo de r_info = tipo
        tocados |= set(range(ins, ins + 4)) | {ent + 4}
    assert all(a == b for i, (a, b) in enumerate(zip(orig, nuevo)) if i not in tocados)


def test_parche_no_deja_reubicaciones_gpio_activas():
    nuevo = modulos.parchear(KO.read_bytes())
    assert all(nuevo[ent + 4] == modulos.R_ARM_NONE for ent, _ in modulos.sitios_gpio(nuevo))
