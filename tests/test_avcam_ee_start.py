"""E2E-9: av-cam (LIRO VM) ante la secuencia real de EE_START de ObjCamera (14 órdenes medidas en el arnés, `tests/avcam_ee_start.json`)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))


def _secuencia() -> list[tuple[int, bytes, bytes]]:
    d = json.loads((ROOT / "tests/avcam_ee_start.json").read_text())
    return [
        (int(m["q"], 16), bytes.fromhex(m["cab"]), bytes.fromhex(m["datos"]))
        for m in d["mensajes"]
    ]


def _corre(grupo: int | None = None):  # noqa: ANN202
    """VM tras entregarle la secuencia (el tiempo virtual avanza 400 ms por orden)."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    P = pytest.importorskip("puente")
    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    vm, t0 = P.arranca()
    vm.limite = t0
    sec = _secuencia()
    for i, (q, cab, datos) in enumerate(sec):
        vm.limite += 400
        L.planifica(vm, 20_000_000)
        if grupo is not None and i == len(sec) - 1:
            vm.wr(0x43EDE338, grupo)  # paso actual del secuenciador de av-cam (lo avanzan los VD del Sync/BONOBO, que la VM no genera)
        m = vm.malloc(max(len(datos), 0x40) + 12 + 0x20) + 12
        vm.uc.mem_write(m - 12, cab)
        vm.uc.mem_write(m, datos)
        vm.msz[m] = len(datos)
        L.entrega(vm, q, m)
    vm.limite += 3000
    L.planifica(vm, 50_000_000)
    return vm


def _respuestas(grupo: int | None = None) -> dict[tuple[int, int], bytes]:
    """{(id, seq): carga} de lo que av-cam emite por 0x20002 tras la secuencia."""
    M = pytest.importorskip("mensajes")
    vm = _corre(grupo)
    out = {}
    for _t, _tarea, _api, q, datos, cab in vm.salida_ext:
        if q == 0x20002 and bytes.fromhex(datos)[:1] == b"\x01":
            r = M.decodifica(bytes.fromhex(datos))
            out[(r.id, r.seq)] = r.carga
    return out


def test_av_cam_contesta_las_ordenes_de_ee_start_con_respuesta() -> None:
    r = _respuestas()
    # EE_START (0x4049 seq 5) y las tres peticiones/ajustes con respuesta: estado 0 y resultado 0xf000 (la `COMP_RESULT` que ObjCamera lee en el CMP)
    for clave in ((0x4049, 5), (0x4036, 11), (0x302A, 13), (0x401B, 14)):
        assert clave in r, f"av-cam no contesta {clave[0]:#x} seq {clave[1]}"
        assert r[clave][:4] == bytes([0x00, 0xF0, 0x00, 0x00])


@pytest.mark.parametrize("grupo", [2, 0x3F, 0x68])
def test_0x3003_se_contesta_si_el_secuenciador_esta_en_el_paso_que_la_espera(grupo: int) -> None:
    """E2E-10 (diagnóstico VERIFICADO): `437fc1b0(0x3003)` devuelve 1 solo con `[0x43ede338]` ∈ {2, 0x3f, 0x68} y entonces `tsk0x61` contesta ya (`43b02740`)."""
    assert (0x3003, 15) in _respuestas(grupo)


@pytest.mark.xfail(
    reason="E2E-10 (T6): con V reales HS_Main corre en cada V, pero la lista del secuenciador (0x43e7e340) nunca se elige: 0x437fc404 sale pronto porque [0x43f9ade8]==0 y nadie lo pone a 1; [0x43ede338] sigue en 0",
    strict=True,
)
def test_av_cam_contesta_0x3003_ultimo_paso_de_ee_start() -> None:
    assert (0x3003, 15) in _respuestas()


def test_bonobo_genera_la_v_y_corre_hs_main_en_cada_v() -> None:
    """E2E-10: la V del sensor (eventos 0x1c/0x1d del BONOBO, INT 0x53) llega a los callbacks de av-cam y SyncTask ejecuta HS_Main (0x4378fef4) en cada V."""
    vm = _corre()
    assert vm.sensor_v.n > 50 and vm.irqs[0x53] >= vm.sensor_v.n
    assert vm.irqs[0x54] > 0  # temporizadores de un disparo armados por av-cam
    assert vm.calls["tsnd_mbf"] > vm.sensor_v.n
