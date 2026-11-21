"""G75 T68 (E2E-15): el DMAC PL080 mueve también memoria → memoria/ventana de registros con cadena LLI y levanta la IRQ de fin."""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))
L = pytest.importorskip("liro_vm")
montura = pytest.importorskip("montura")
CTRL = 0xF0103000  # canal 8 = controlador 1, canal 0


@pytest.fixture(scope="module")
def vm():
    if not L.AVCAM.exists():
        pytest.skip("falta av-cam.bin")
    v = L.carga(L.AVCAM, L.BK, None)
    v.uart = montura.instala(v)
    return v


def test_cadena_lli_memoria_a_memoria_copia_y_avisa_en_el_ultimo_elemento(vm) -> None:
    """VERIFICADO en bytes: el driver RC vertical (id 9) programa el canal 8 (`0x4398f454`) con control `0x0e489001` (sin I) y LLI al siguiente elemento; PL080: TC solo si el control del elemento lleva I (bit 31)."""
    a, b, d = vm.malloc(64), vm.malloc(64), vm.malloc(64)
    vm.uc.mem_write(a, struct.pack("<2I", 0x11111111, 0x22222222))
    vm.uc.mem_write(b, struct.pack("<I", 0x33333333))
    lli2 = vm.malloc(16)
    vm.uc.mem_write(lli2, struct.pack("<4I", b, d + 8, 0, 0x8E489001))  # último elemento, I=1, 1 palabra
    ch = CTRL + 0x100
    for off, v in ((0, a), (4, d), (8, lli2), (0xC, 0x0E489002), (0x10, 0x1000001)):
        vm.wr(ch + off, v)
    vm.uart.dmac._escribe(vm.uc, 0, ch + 0x10, 4, 0x1000001, CTRL)
    vm.uart.avanza(vm)
    assert bytes(vm.uc.mem_read(d, 12)) == struct.pack("<3I", 0x11111111, 0x22222222, 0x33333333)
    assert not vm.rd(ch + 0x10) & 1  # el hardware baja el habilitado al acabar
    assert vm.lineas[0xB5]()  # IRQ del canal 8 = 0xad + 8


E68 = ROOT / "analysis/gui/g22/harness/live/e2e68/avcam.jsonl"


@pytest.mark.skipif(not E68.exists(), reason="falta la sesión e2e68 (no versionada)")
def test_driver_rc_directo_libera_su_ranura_con_el_fin_de_la_cadena_del_dmac() -> None:
    """Réplica de e2e68 con el Master del reloj: el driver RC vertical (id 9, petición «directa») deja la ranura en 4 salvo que el fin de la cadena del DMAC levante su IRQ; sin ello (`AVCAM_RC_DIRECTO=0`) `[RC] request = NULL` se repite en cada trama."""
    import os
    import subprocess

    def corre(directo: str) -> int:
        env = {**os.environ, "AVCAM_RELOJ": "1", "AVCAM_RC_DIRECTO": directo}
        out = subprocess.run([sys.executable, str(ROOT / "scripts/gui/avcam/master_diag.py"), str(E68), "reloj", "13800", "14500"], env=env, capture_output=True, text=True, timeout=900, check=True).stdout
        return int(out.split("RC request = NULL:")[1].split()[0])

    con, sin = corre("1"), corre("0")
    assert con <= 4 and sin >= 20
