"""G75 T67 (E2E-15): fin de trabajo del acelerador Spica (cola de 2 ranuras de `SpicaApiExpandParam`/`Execute`)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))
L = pytest.importorskip("liro_vm")
BASE = 0xF3810000


@pytest.fixture(scope="module")
def vm():
    if not L.AVCAM.exists():
        pytest.skip("falta av-cam.bin")
    return L.carga(L.AVCAM, L.BK, None)


def test_arranque_de_spica_levanta_el_fin_de_execute_y_el_ack_lo_baja(vm) -> None:
    """VERIFICADO en bytes: arranque `base+0x20`=1, estado `+0x10` (0x10 Execute, 0x1000 Expand), ack escribiendo lo leído en `+0x14`, máscara `+0x18`, IRQ 0x51."""
    vm.wr(BASE + 0x18, 0x11010)
    assert not vm.lineas[0x51]()
    s = vm.spica
    s._escribe(vm.uc, 0, BASE + 0x20, 4, 1, BASE)  # lo que llama el gancho de escritura de Unicorn
    assert not vm.lineas[0x51]() and s.prox is not None
    vm.t = s.prox
    s.avanza(vm)
    assert vm.lineas[0x51]() and not vm.lineas[0x52]()
    s._lee(vm.uc, 0, BASE + 0x10, 4, 0, BASE)
    assert vm.rd(BASE + 0x10) == 0x1010
    s._escribe(vm.uc, 0, BASE + 0x14, 4, 0x1010, BASE)
    assert not vm.lineas[0x51]()


E68 = ROOT / "analysis/gui/g22/harness/live/e2e68/avcam.jsonl"


@pytest.mark.skipif(not E68.exists(), reason="falta la sesión e2e68 (no versionada)")
def test_expand_param_no_devuelve_4_con_el_fin_de_trabajo() -> None:
    """Réplica con el Master del modelo de reloj: con Spica el fin vacía la cola y `SpicaApiExpandParam error!` (código 4) no aparece; sin él (`AVCAM_SPICA=0`) aparece en cada trama."""
    def corre(spica: str) -> str:
        env = {**os.environ, "AVCAM_RELOJ": "1", "AVCAM_SPICA": spica}
        return subprocess.run([sys.executable, str(ROOT / "scripts/gui/avcam/master_diag.py"), str(E68), "reloj", "13800", "17000"], env=env, capture_output=True, text=True, timeout=900, check=True).stdout
    assert "SpicaApiExpandParam error: 0" in corre("1")
    assert "SpicaApiExpandParam error: 0" not in corre("0")


def test_rc_el_fin_del_dma_borra_ocupado_sube_estado_y_levanta_la_irq_del_driver(vm) -> None:
    """VERIFICADO en bytes (g75 T67): control `0xf3881000+((c+4)<<7)`, estado por nibble en `+0x1000`, máscara `+0x1008`; el ISR de cada id está cableado a su driver (`IRQ_ID`)."""
    import rc
    r = vm.rc
    vm.wr(rc.MASCARA, 0xF0)  # nibble del canal 1
    vm.wr(0xF3881280, 3)
    r._inicio(vm.uc, 0, 0xF3881280, 4, 3, 1)
    r.ini[0] = r.ini[1]
    vm.t = r.prox
    r.avanza(vm)
    assert vm.rd(0xF3881280) & 1 == 0 and r.estado == 0xF0
    r.pend.add(8)
    assert vm.lineas[rc.IRQ_ID[8]]() and not vm.lineas[rc.IRQ_ID[8]]()  # pulso: una sola vez
    r._ack(vm.uc, 1, rc.ESTADO, 4, 0xF0, None)
    assert r.estado == 0
