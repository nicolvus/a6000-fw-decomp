"""LIRO VM (scripts/gui/avcam/liro_vm.py): av-cam.bin arranca con la API de liro.ko emulada (paso 1 de la emulación de av-cam)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AVCAM = ROOT / "scripts/gui/avcam"


def _vm():
    pytest.importorskip("unicorn")
    sys.path.insert(0, str(AVCAM))
    spec = importlib.util.spec_from_file_location("liro_vm", AVCAM / "liro_vm.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["liro_vm"] = m  # dataclasses necesita el módulo registrado
    spec.loader.exec_module(m)
    if not m.AVCAM.exists() or not m.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    return m


def test_tabla_api_de_liro_ko() -> None:
    """La tabla de 209 entradas sale de .rel.init.data de liro.ko: μITRON 4 + OSAL + Backup, en ese orden."""
    m = _vm()
    n = m.api_names()
    assert len(n) == 209 and n[0] == "CRE_TSK" and n[0x1B0 // 4] == "osal_snd_msg" and n[0x274 // 4] == "Backup_read"


def test_avcam_arranca_hasta_el_reposo() -> None:
    """entry(pre) + entry(main): crea sus 113 tareas, registra colas OSAL, escribe «Liro Start» y queda en reposo (todas esperando)."""
    m = _vm()
    vm = m.carga(m.AVCAM, m.BK)
    m.crea_tarea(vm, 1, "entry_pre", 0x43541044, 0, 0).estado = "lista"
    m.planifica(vm, 2_000_000)
    m.crea_tarea(vm, 2, "entry_main", 0x43541058, 0, 0).estado = "lista"
    m.planifica(vm, 200_000_000)
    assert vm.calls["CRE_TSK"] == 113 and len(vm.qcb) >= 50
    assert any("[CAMERA_MAIN]: Liro Start" in x for x in vm.log)
    assert not [x for x in vm.tasks.values() if x.estado == "lista"]
    assert not [x for x in vm.log if "ERROR" in x], "ninguna tarea cae (buffers mbf, pilas por tarea, DMM +8/+0xc, reloj, FIFO)"
    assert any(x.estado == "espera" and x.espera[:2] == ("rcv", 0x30001) for x in vm.tasks.values()), "CamMgr (cola 0x30001) espera mensajes"
