"""G83/G84 — parche de niveles de Zebra (scripts/gui/zebra_levels_patch.py): 1 byte por índice, sale de fábrica, rechaza ficheros ajenos."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import zebra_levels_patch as z

SO = ROOT / "analysis/camera-extract/usr/lib/libObj.so"


@pytest.mark.skipif(not SO.exists(), reason="libObj.so extraído no disponible")
def test_fabrica_y_parche_de_un_byte_por_indice():
    d = SO.read_bytes()
    assert [d[a] for a in z.SITIOS] == z.FABRICA
    out = z.patch(d, [10, *z.FABRICA[1:]])
    assert [i for i in range(len(d)) if d[i] != out[i]] == [z.SITIOS[0]] and out[z.SITIOS[0]] == 10
    assert z.patch(out, z.FABRICA) == d
    with pytest.raises(AssertionError):
        z.patch(d, [200, *z.FABRICA[1:]])
    with pytest.raises(AssertionError):
        z.patch(d[: z.SITIOS[0] + 1] + b"\0" + d[z.SITIOS[0] + 2:], z.FABRICA)
