"""G116 (LUT-C, cierre estático) — reubicación del ajuste LUT fuera de `ZONA_A`/`ZONA_B` y escáner de referencias que lo justifica.

`ZONA_A` es la tabla T1 de estabilización y `ZONA_B` las tablas BOKS del YC (G107 §3): el parche histórico de la LUT escribía en memoria viva.
Ahora cueva, máquina y curva viven en la cola libre de G18 (`ZONA_L18`/`ZONA_T18`) y las tablas salen del blob de la SD (G89), así que el `.dat`
no necesita tablas. Este test comprueba el escáner (`zonas.py`) contra referencias conocidas y que el parche no toca ni una byte de A/B.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut")]
import avcam_dinamico as D
import cube_a6000 as C
import lut_patch as P
import lut_t as T
import zonas as Z

pytestmark = pytest.mark.skipif(not C.BIN.is_file(), reason="av-cam.bin ausente")


@pytest.fixture(scope="module")
def img():
    return C.BIN.read_bytes()


@pytest.fixture(scope="module")
def parche(img):
    return P.apply_bytes(img)


def test_el_escaner_encuentra_las_referencias_conocidas(img):
    """Control positivo: la tabla T1 (`ZONA_A`) y las BOKS (`ZONA_B`) sí están referenciadas, y el escáner las ve."""
    assert (0x43705A3C, "ldr+add", D.ZONA_A[0]) in Z.referencias(img, *D.ZONA_A)
    boks = {a for a, _, _ in Z.referencias(img, *D.ZONA_B)}
    assert {0x438F6FBA, 0x438F6FD2} <= boks


@pytest.mark.parametrize("zona", ["ZONA_L18", "T18"])
def test_las_zonas_nuevas_no_tienen_referencias(img, zona):
    z = D.ZONA_L18 if zona == "ZONA_L18" else T.ZONA_T18
    libre, refs = Z.libre(img, z)
    assert libre, [(hex(a), t, hex(v)) for a, t, v in refs]


def test_el_parche_no_escribe_en_la_tabla_t1_ni_en_las_boks(img, parche):
    dif = [i + P.BASE for i in range(len(img)) if img[i] != parche[i]]
    assert dif and not any(any(z[0] <= a < z[1] for z in (D.ZONA_A, D.ZONA_B)) for a in dif)
    assert not any(0x43D620D9 <= a < 0x43FA8F00 for a in dif)          # zona viva de G72


def test_todo_cabe_en_la_cola_libre_de_g18(img, parche):
    """Cueva + celda + máquina en `ZONA_L18` y celda + curva en `ZONA_T18`; las dos dentro del hueco G18 verificado."""
    esc = P.cueva_maquina()[1] + [(D.LUT_CELDA, bytes(8))] + T.escrituras(P.AJ_SD)[0]
    cueva, _ = D.lut_codigo(P.AJ_SD, P.HOOKS)
    esc += cueva
    for a, b in esc:
        assert any(z[0] <= a and a + len(b) <= z[1] for z in (D.ZONA_L18, T.ZONA_T18)), hex(a)
    for z in (D.ZONA_L18, T.ZONA_T18):
        assert D.ZONA_G18[0] <= z[0] < z[1] <= D.ZONA_G18[1]
    ocupado = sum(len(b) for a, b in esc if D.ZONA_L18[0] <= a < D.ZONA_L18[1])
    assert ocupado <= D.ZONA_L18[1] - D.ZONA_L18[0]
