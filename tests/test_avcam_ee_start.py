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


def _respuestas(grupo: int | None = None) -> dict[tuple[int, int], bytes]:
    """{(id, seq): carga} de lo que av-cam emite por 0x20002 tras entregarle la secuencia (el tiempo virtual avanza 400 ms por orden)."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    P = pytest.importorskip("puente")
    M = pytest.importorskip("mensajes")
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
    reason="E2E-10: en frío `[0x43ede338]` = 0 y av-cam deja armada la 0x3003 (estado 1) hasta que el secuenciador de HS_Main (VD del Sync/BONOBO, sin modelar en la VM) llegue a un paso 2/0x3f/0x68",
    strict=True,
)
def test_av_cam_contesta_0x3003_ultimo_paso_de_ee_start() -> None:
    assert (0x3003, 15) in _respuestas()
