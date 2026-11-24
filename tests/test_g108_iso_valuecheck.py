"""G108 — bucle de arranque de la build `iso`: el validador de `libObj` (G107) rechazaba los VALUEID ISO 128000…409600 del CFW.

Con el ISO guardado en 128000+ (registro `0x10700c1`, código `0x4b…0x50`), `iso_libobj_patch` lo convierte en VALUEID `0x3fd…0x3ff`/`0x50e…0x510`, que no
están en las listas de `PARAMID_ISO_SPEED_RATE_SET`/`_ACT`/`_MIN`/`_MAX`: en el arnés la app no manda ninguna orden a av-cam (ni el paquete de arranque
`0x4074`). Tras el arreglo, todas esas listas los admiten (Unicorn sobre la definición real `0x95aca8`).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
sys.path.insert(0, str(ROOT / "tests"))
from test_g25_gamma_libobj import LIB, needs
from test_g107_pp_valuecheck import definicion

ISO_PIDS = (0x951E, 0x96FE, 0x96FF, 0x9700, 0x9701, 0x9702, 0x9703, 0x9704, 0x9705)


@needs
def test_fabrica_rechaza_iso_128000_en_la_orden():
    assert 0x3FF not in definicion(LIB.read_bytes(), 0x9700)[1]


@needs
def test_listas_iso_admiten_los_valueid_del_cfw():
    import iso_libobj_patch as I
    fab = LIB.read_bytes()
    d = I.patch(fab)
    for pid in ISO_PIDS:
        vieja, nueva = definicion(fab, pid)[1], definicion(d, pid)[1]
        assert nueva[:len(vieja)] == vieja and set(I.VALUEIDS) <= set(nueva), hex(pid)
    assert definicion(d, 0x9673) == definicion(fab, 0x9673)                    # Color Mode de PP no cambia
