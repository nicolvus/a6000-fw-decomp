import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / 'scripts' / 'usb_carga'))
import chg_ic_set as c


def test_preajustes_reproducen_los_valores_de_darwin():
    assert c.carga_util('carga', 1500) == bytes([2, 0xC9, 4]) + bytes(5)   # 0xc4e8(1,0xc0,4) | bit 3
    assert c.carga_util('normal', 100) == bytes([0, 0x0A, 0]) + bytes(5)   # «Off exit» 0xc4e8(2,0,0) | bit 3


def test_limites_siguen_la_tabla_de_0xc6f0():
    assert [c.LIMITE[m] for m in (100, 500, 1500, 900, 2000)] == [0, 1, 2, 3, 4]


@pytest.mark.parametrize('modo,ma', [('carga', 700), ('otro', 500)])
def test_rechaza_valores_fuera_de_tabla(modo, ma):
    with pytest.raises(ValueError):
        c.carga_util(modo, ma)
