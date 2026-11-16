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


def _corre(grupo: int | None = None, pre=None):
    """VM tras entregarle la secuencia (el tiempo virtual avanza 400 ms por orden); `pre(vm)` instala ganchos de diagnóstico tras el arranque."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    P = pytest.importorskip("puente")
    if not L.AVCAM.exists() or not L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    vm, t0 = P.arranca()
    vm.limite = t0
    if pre:
        pre(vm)
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


def test_paridad_de_v_hace_que_vd_pre_refresque_la_tabla_de_destinos_g() -> None:
    """E2E-10 (T9, MEDIDO): VD_Pre (`0x43792a0c`) solo copia los destinos del secuenciador (`437fc54c(n)`) en `G=0x43e9b548` (`0x43792e8e…0x43792ef6`) si el bit 0 de `0xf3402028`
    (leído por `0x43b4c2fc` a `[[0x43e99208+4]+0xc]`) vale 1 o el retardo `[G+0x5d0]` ≤ 1; con la paridad de V (`bonobo.REG_PARIDAD`) G recibe los destinos del guion 0→2 y los
    módulos 6, 8 y 9 (`0x43e9cf04`, `0x43e9d018`, `0x43eb3d20`) llegan a 0x780/0x910/0xa10; los módulos 0, 1 y 2 siguen parados (ver el xfail)."""
    vm = _corre()
    G = 0x43E9B548
    assert [vm.rd(G + 2 * k, 2) for k in (0, 1, 2, 6, 7, 8)] == [0x105, 0x320, 0x285, 0x780, 0x910, 0xA10]
    assert [vm.rd(a, 2) for a in (0x43E9CF04, 0x43E9D018, 0x43EB3D20)] == [0x780, 0x910, 0xA10]
    assert [vm.rd(a, 2) for a in (0x43E9BD58, 0x43EC7ADC, 0x43E9C7D8)] == [0x100, 0x200, 0]


def test_eslabon_clkctrl_la_transicion_del_modulo_0_espera_el_vfc_del_maestro() -> None:
    """E2E-10 (T9, MEDIDO): con G[0]=0x105 la máquina `0x43796954` solo avanza si `[0x43e991d8]`=`[G+0x778]` (=1); `0x43e991d8` se carga de `0x43e991dc` cuando `[0x43e991d0]`==0, pero `0x4378e0fc`
    pone `[0x43e991d0]`=-1 porque `[0x43e4a5c0]` (targetVfc de `[CLK_CTRL]`, el que fija `0x435a0596` al recibir el mensaje `0x80c001bd` «from Master») sigue en su valor inicial 0xffff0000."""
    vm = _corre()
    assert vm.rd(0x43E991D0) == 0xFFFFFFFF and vm.rd(0x43E991D8) == 0 and vm.rd(0x43E991DC) == 1 and vm.rd(0x43E9B548 + 0x778) == 1
    assert vm.rd(0x43E4A5C0) == 0xFFFF0000


def test_puente_vigila_registra_escrituras_del_rango(tmp_path, monkeypatch) -> None:
    """`AVCAM_VIGILA=dir:tam` (diagnóstico, desactivado por defecto) anota cada escritura con su pc y valor en el registro."""
    P = pytest.importorskip("puente")
    if not P.L.AVCAM.exists() or not P.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    monkeypatch.setenv("AVCAM_VIGILA", "43e9b548:60")
    reg = tmp_path / "avcam.jsonl"
    pu = P.Puente(lambda _l: None, reg)
    try:
        with pu.cerrojo:  # el hilo del reloj usa la misma VM
            pu.vm.limite = pu.vm.t + 200
            P.L.planifica(pu.vm, 20_000_000)
    finally:
        pu.cierra()
    filas = [json.loads(x) for x in reg.read_text().splitlines()]
    assert any(f.get("vigila") and f["pc"].startswith("0x43792d") for f in filas)


@pytest.mark.xfail(
    reason="E2E-10 (T9, g75 «Tarea 9»): el secuenciador elige 0→2 pero se queda en la barrera 0x8347: con la paridad de V los módulos 6, 8 y 9 llegan a su destino, pero el 0 espera `[0x43e991d8]`=1 (ClkCtrl: falta el mensaje `0x80c001bd` del «Master») y los 1 y 2 dependen de sus propias máquinas de estado",
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


def test_secuenciador_elige_la_transicion_0_a_2_y_espera_el_estado_de_los_modulos() -> None:
    """E2E-10 (T7, MEDIDO): la 0x3003 arma `437fc35c` (pone `[0x43f9ade8]`=1, no es un requisito previo); en la V siguiente `437fc404` fija el destino 2, `43b006d0` halla la fila {0→2} (guion `0x43bf2208`, 0x2b palabras) y el guion
    se detiene en su primera barrera: las palabras de estado de los módulos (`0x43e9bd58`…) no llegan a lo que pide el guion."""
    vm = _corre()
    lista = 0x43EDE340  # {tabla, n filas, …, +0xc activo, +0x10 guion, +0x14 largo, +0x18 posición, +0x1c destino por slot}
    assert vm.rd(0x43F9ADE8, 1) == 1 and vm.rd(0x43EDE320) == 2 and vm.rd(lista + 0xC, 1) == 1 and vm.rd(lista + 0x10) == 0x43BF2208
    assert vm.rd(0x43EDE338) == 0 and vm.rd(lista + 0x18) == 12  # parado en la primera barrera
    estado = {0: 0x43E9BD58, 2: 0x43E9C7D8, 8: 0x43E9D018}
    assert {j: vm.rd(a, 2) for j, a in estado.items()} == {0: 0x100, 2: 0, 8: 0x910}  # T9: el 8 ya alcanza su destino con la paridad de V
    assert [vm.rd(lista + 0x1C + 2 * j, 2) for j in estado] == [0x105, 0x320, 0x910]


def test_eventos_1e_y_17_de_captura_llegan_a_sus_callbacks_y_el_modulo_1_escribe_su_estado() -> None:
    """E2E-10 (T8, MEDIDO): av-cam registra en el primer VD los eventos BONOBO 0x1e (`0x437918ac` → encola `0x4379155c`) y 0x17 (`0x4378f2cc`); con ellos corre el escritor del slot 0 (`0x437916dc`), que
    escribe el estado calculado por `0x43796954` (0x100: la máquina de estados lo deja igual mientras su petición `G[0]` valga 0x100, así que no basta para 0x105)."""
    pytest.importorskip("unicorn")
    from collections import Counter

    from unicorn import UC_HOOK_CODE

    cuenta: Counter = Counter()

    def pre(vm) -> None:
        def h(uc, a, s, _) -> None:
            cuenta[a] += 1

        for a in (0x437918AC, 0x4378F2CC, 0x4379155C, 0x437916DC):
            vm.uc.hook_add(UC_HOOK_CODE, h, None, a, a)

    vm = _corre(pre=pre)
    assert all(cuenta[a] > 30 for a in (0x437918AC, 0x4378F2CC, 0x4379155C, 0x437916DC))
    assert vm.rd(0x43E9BD58, 2) == 0x100


def test_diagnostico_si_las_palabras_de_estado_alcanzan_el_guion_0_a_2_completa_y_av_cam_contesta_0x3003() -> None:
    """E2E-10 (T8, DIAGNÓSTICO, no es arreglo): `HS_Main` lee el estado de cada slot con `437fc56c(slot, estado)` (`0x437906e4…`). Forzando r1 = destino del guion en esa llamada (como si los 11 módulos de imagen hubieran
    llegado a su estado), el guion 0→2 recorre sus 7 barreras (posición 42 de 43), `[0x43ede338]`=2 y av-cam contesta `{1,0x3003,15}`: no hay más requisitos ocultos tras los módulos."""
    pytest.importorskip("unicorn")
    from unicorn import UC_HOOK_CODE
    from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1

    lista = 0x43EDE340

    def pre(vm) -> None:
        def h(uc, a, s, _) -> None:
            d = vm.rd(lista + 0x1C + 2 * uc.reg_read(UC_ARM_REG_R0), 2)
            if d:
                uc.reg_write(UC_ARM_REG_R1, d)

        vm.uc.hook_add(UC_HOOK_CODE, h, None, 0x437FC56C, 0x437FC56C)

    vm = _corre(pre=pre)
    assert vm.rd(lista + 0x18) == 42 and vm.rd(0x43EDE338) == 2
    M = pytest.importorskip("mensajes")
    ids = {M.decodifica(bytes.fromhex(x[4])).id for x in vm.salida_ext if x[3] == 0x20002 and bytes.fromhex(x[4])[:1] == b"\x01"}
    assert 0x3003 in ids
