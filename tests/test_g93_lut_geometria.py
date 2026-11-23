"""G93 — la rejilla 5×9×9 es del IP de la LUT (igual en A6000/A7S/A6300) y 17³ no cabe en sus SRAM."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C

ENT = ROOT / "analysis/rea-independent/input"
ESCRITOR = 0x43B67918                            # 8 bloques fijos a HW+0x17000…0x17800 (tbb de 8 casos, 0x6a B)
VENTANA = [128, 64, 64, 64, 64, 64, 64, 512]     # palabras máximas por banco según el mapa (paso 0x200/0x100; el 7 hasta 0x17fff)


def bancos(ny: int, nc: int) -> list[int]:
    """Palabras por banco de paridad (j, a, b) en el orden del HW para una rejilla ny×nc×nc."""
    par = [(n + 1) // 2 for n in (ny, nc, nc)]
    imp = [n // 2 for n in (ny, nc, nc)]
    return [(par[0], imp[0])[j] * (par[1], imp[1])[a] * (par[2], imp[2])[b]
            for j in (0, 1) for a in (0, 1) for b in (0, 1)]


def cabe(ny: int, nc: int) -> bool:
    return all(n <= v for n, v in zip(bancos(ny, nc), VENTANA))


@pytest.mark.parametrize("modelo", ["av-cam-a7s.bin", "av-cam-a6300.bin"])
def test_mismo_ip_en_otros_modelos(modelo):
    if not (C.BIN.exists() and (ENT / modelo).exists()):
        pytest.skip("faltan los binarios")
    a, b = C.BIN.read_bytes(), (ENT / modelo).read_bytes()
    assert b.find(a[C.PERM - C.BASE:C.PERM - C.BASE + 810]) >= 0              # permutación de 405 nodos
    assert b.find(a[ESCRITOR - C.BASE:ESCRITOR - C.BASE + 0x6A]) >= 0          # escritor con los mismos tamaños


def test_capacidad_de_las_sram():
    assert bancos(5, 9) == [75, 60, 60, 48, 50, 40, 40, 32] and cabe(5, 9)
    assert not cabe(6, 9) and not cabe(5, 10)                                   # 5×9×9 es el máximo del mapa
    assert not cabe(9, 9) and not cabe(17, 17)
    assert 17 ** 3 > sum(VENTANA)                                               # ni sumando toda la ventana
