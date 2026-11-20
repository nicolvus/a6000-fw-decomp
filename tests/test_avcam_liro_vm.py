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


def test_monton_reutiliza_los_bloques_liberados() -> None:
    """E2E-16: el montón de 240 MiB era un puntero que solo crecía (liro_free/osal_free_msg/rel_mpf eran no-ops) y se agotaba a los ≈7 min."""
    L = _vm()
    vm = L.carga(L.AVCAM, L.BK)
    a = vm.malloc(100)
    vm.free(a)
    vm.free(a)  # doble liberación: se ignora
    assert vm.malloc(100) == a and vm.malloc(100) != a
    h = vm.heap
    for _ in range(10_000):
        vm.free(vm.malloc(0x800 + 12))
    assert vm.heap - h <= 0x1000
    vm.free(0x1234)  # puntero ajeno: se ignora


def test_patron_se_aplica_por_pagina_sin_ganchos_masivos() -> None:
    """LIRO-VEL-1: Unicorn recorre todos los ganchos de lectura en cada carga; el patrón (+4 → bit 0 puesto) se instala solo en las páginas mapeadas."""
    m = _vm()
    vm = m.carga(m.AVCAM, m.BK)
    vm.uc.mem_map(0xF2A07000, 0x1000)
    vm.patron_pagina(0xF2A07000)
    assert int.from_bytes(vm.uc.mem_read(0xF2A07004, 4), "little") == 1
    assert int.from_bytes(vm.uc.mem_read(0xF2A07030, 4), "little") == 0


def test_la_vm_no_va_mas_lenta_que_3_veces_el_tiempo_real() -> None:
    """LIRO-VEL-1: antes ≈ 5,6× más lenta que el tiempo real (reposo tras el arranque); ahora ≈ 1×. Cota floja para no fallar con la máquina cargada."""
    import time

    import puente as P

    _vm()
    vm, _ = P.arranca()
    vm.limite = vm.t + 1500
    t0, v0 = time.time(), vm.t
    P.L.planifica(vm, 2_000_000_000)
    assert (time.time() - t0) / ((vm.t - v0) / 1000) < 3.0
