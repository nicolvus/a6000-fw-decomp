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
    módulos 6, 8 y 9 (`0x43e9cf04`, `0x43e9d018`, `0x43eb3d20`) llegan a 0x780/0x910/0xa10. T14: con `Backup_read_multi` también el 0 y el 1 (0x105/0x285); solo el bloque
    del módulo 3 (`0x43e9c7d8`, destino 0x320; 0x301 en el volcado real) sigue a 0 (ver el xfail)."""
    vm = _corre()
    G = 0x43E9B548
    assert [vm.rd(G + 2 * k, 2) for k in (0, 1, 2, 6, 7, 8)] == [0x105, 0x320, 0x285, 0x780, 0x910, 0xA10]
    assert [vm.rd(a, 2) for a in (0x43E9CF04, 0x43E9D018, 0x43EB3D20)] == [0x780, 0x910, 0xA10]
    assert [vm.rd(a, 2) for a in (0x43E9BD58, 0x43EC7ADC, 0x43E9C7D8)] == [0x105, 0x285, 0]


def test_clkctrl_sin_master_con_backup_real_coincide_con_la_camara() -> None:
    """E2E-10 (T14, MEDIDO; corrige T9/T13): el bloqueo del módulo 0 por ClkCtrl era un síntoma de `Backup_read_multi` sin modelar. Con él, `[0x43e4a5c0]` (targetVfc) vale 0xffffffff
    —el mismo valor que en el volcado real `ram-servicio-20261020`—, `[0x43e991d0]`=0 y el módulo 0 llega a 0x105 sin ningún mensaje «from Master»."""
    vm = _corre()
    assert vm.rd(0x43E4A5C0) == 0xFFFFFFFF and vm.rd(0x43E991D0) == 0
    assert vm.rd(0x43E9BD58, 2) == 0x105


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
    reason="E2E-10 (T14, g75 «Tarea 14»): el guion 0→2 sigue en la barrera 0x8347 solo por el slot 2: el bloque del módulo 3 (`0x43e9c7d8`, destino 0x320; 0x301 en el volcado real) no lo rellena nadie en la VM; los slots 0, 1, 6, 8 y 9 ya llegan",
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
    estado = {0: 0x43E9BD58, 1: 0x43EC7ADC, 2: 0x43E9C7D8, 8: 0x43E9D018}
    assert {j: vm.rd(a, 2) for j, a in estado.items()} == {0: 0x105, 1: 0x285, 2: 0, 8: 0x910}  # T14: solo el slot 2 (bloque del módulo 3) no llega
    assert [vm.rd(lista + 0x1C + 2 * j, 2) for j in estado] == [0x105, 0x285, 0x320, 0x910]


def test_eventos_1e_y_17_de_captura_llegan_a_sus_callbacks_y_el_modulo_1_escribe_su_estado() -> None:
    """E2E-10 (T8, MEDIDO): av-cam registra en el primer VD los eventos BONOBO 0x1e (`0x437918ac` → encola `0x4379155c`) y 0x17 (`0x4378f2cc`); con ellos corre el escritor del slot 0 (`0x437916dc`), que
    escribe el estado calculado por `0x43796954` (T14: con `Backup_read_multi` llega a su destino 0x105)."""
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
    assert vm.rd(0x43E9BD58, 2) == 0x105


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


def _s1_s2(lock: int | None) -> tuple[list[str], dict[tuple[int, int], bytes]]:
    """T10: tras EE_START (+ `0x3003`), las 8 órdenes de S1 y la `0x4044` de S2 medidas en vivo; `lock` = `[0x43e94eec]` (bandera «LOCK» del módulo de disparo) antes de S2."""
    M = pytest.importorskip("mensajes")
    L = pytest.importorskip("liro_vm")
    vm = _corre(2)
    n0 = len(vm.log)
    for m in json.loads((ROOT / "tests/avcam_s1_s2.json").read_text())["mensajes"]:
        cab, datos = bytes.fromhex(m["cab"]), bytes.fromhex(m["datos"])
        if lock is not None and datos[2:4] == b"\x44\x40":
            vm.wr(0x43E94EEC, lock)
        vm.limite += 300
        p = vm.malloc(max(len(datos), 0x40) + 12 + 0x20) + 12
        vm.uc.mem_write(p - 12, cab)
        vm.uc.mem_write(p, datos)
        vm.msz[p] = len(datos)
        L.entrega(vm, int(m["q"], 16), p)
        L.planifica(vm, 20_000_000)
    vm.limite += 3000
    L.planifica(vm, 50_000_000)
    r = {}
    for _t, _tarea, _api, q, d, _cab in vm.salida_ext:
        if q == 0x20002 and bytes.fromhex(d)[:1] == b"\x01":
            x = M.decodifica(bytes.fromhex(d))
            r[(x.id, x.seq)] = x.carga
    return vm.log[n0:], r


def test_s1_se_contesta_y_s2_avisa_de_lock_no_retenido() -> None:
    """E2E-3 (MEDIDO en vivo y aquí): las dos `0x4049` de S1 se contestan con `0xf000`; la `0x4044` de S2 solo dispara el aviso `RelLock) You may forget to hold down the LOCK key` porque `[0x43e94eec]` (leído solo en `0x4381d0ca`, nadie lo escribe en este flujo) vale 0; con 1 el aviso desaparece."""
    log, r = _s1_s2(None)
    assert sum(1 for (i, _s) in r if i == 0x4049) >= 2
    assert any("RelLock) You may forget to hold down the LOCK key" in x for x in log)
    log1, _ = _s1_s2(1)
    assert not any("RelLock)" in x for x in log1)


def _s2_gate(forzar: bool) -> dict:
    """T11: reproduce S1 completo + `0x4044` y mide la puerta de la petición de captura de RelMgr: cuántas veces corre el emisor de `0x3011` (`0x4379eba0`) y qué valen los factores de bloqueo. `forzar` fuerza (DIAGNÓSTICO, no es un arreglo fiel) `[RelMgr+0xbe8]=-1` y la ranura 1 del objeto de bloqueos."""
    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    from unicorn import UC_HOOK_CODE

    vm = _corre(2)
    ms = json.loads((ROOT / "tests/avcam_s1_s2.json").read_text())["mensajes"]
    assert ms[16]["datos"][:8] == "05004440", "el 17º mensaje debe ser la 0x4044"
    obj = 0x43EA03E8  # RelMgr+0xbe4: objeto de bloqueos (vtable 0x43fcd5f0)
    cuenta = {"eba0": 0, "d088": 0, "warn": 0}

    def h(_uc, a, _s, _u) -> None:
        for k, v in (("eba0", 0x4379EBA0), ("d088", 0x4381D088), ("warn", 0x4381CFC0)):
            if a == v:
                cuenta[k] += 1

    def entrega(m: dict) -> None:
        cab, datos = bytes.fromhex(m["cab"]), bytes.fromhex(m["datos"])
        vm.limite += 300
        p = vm.malloc(max(len(datos), 0x40) + 12 + 0x20) + 12
        vm.uc.mem_write(p - 12, cab)
        vm.uc.mem_write(p, datos)
        vm.msz[p] = len(datos)
        L.entrega(vm, int(m["q"], 16), p)
        L.planifica(vm, 20_000_000)

    for m in ms[:16]:
        entrega(m)
    estado = {"mascara": vm.rd(obj + 4), "ranuras": [vm.rd(obj + o) for o in (0x48, 0x4C, 0x50)], "d1": vm.rd(0x43E95950 + 0xD1, 1)}
    if forzar:
        vm.wr(obj + 4, 0xFFFFFFFF)
        vm.wr(obj + 0x4C, 1)
    vm.uc.hook_add(UC_HOOK_CODE, h, begin=0x4379EBA0, end=0x4381D088 + 8)
    n0 = len(vm.log)
    entrega(ms[16])
    vm.limite += 3000
    L.planifica(vm, 50_000_000)
    return {**estado, **cuenta, "setup_err": any("SetupTable" in x for x in vm.log[n0:])}


def test_s2_la_peticion_de_captura_se_deniega_por_dos_factores_de_bloqueo() -> None:
    """E2E-3/T11 (MEDIDO): con S1 hecho y `0x4044`, `0x4381d088` (RelLock) niega la petición: la máscara de factores `[RelMgr+0xbe8]` vale `0xfbffffbf` (factores 6 y 26 activos; permitir exige `==-1`), las ranuras 0..2 y el byte `[0x43e95950+0xd1]` valen 0 (de ahí el aviso) y `0x4379eba0` (emisor de `0x3011`) no corre. Forzando máscara y ranura la petición pasa (`0x3011` sale), pero el secuenciador sigue rechazando `SetupTable` (modo de captura, T9)."""
    base = _s2_gate(False)
    assert base["mascara"] == 0xFBFFFFBF and base["mascara"] & 0x04000040 == 0
    assert base["ranuras"] == [0, 0, 0] and base["d1"] == 0
    assert base["d088"] == 1 and base["warn"] == 1 and base["eba0"] == 0
    forz = _s2_gate(True)
    assert forz["eba0"] == 1 and forz["warn"] == 0
    assert forz["setup_err"]


def test_factor_26_lo_libera_initend_de_capidtblmgr_y_el_6_depende_del_modo() -> None:
    """E2E-3/T12 (MEDIDO): `0xd013` lo emite el CapIdTblMgr de av-cam (tsk0x5b, cola `0x4015e`, tabla `0x43bf3800`: clave `0x1003`→`0xd013`) al recibir `InitEnd` de libObj (`CapIdTableAcsr::InitEnd` `libObj+0x81c25c`). Con ella el factor 26 se libera; `0x1000/1/2` se contestan por la cola de respuesta y StartAccess/StopAccess mueven el factor 11. El factor 6 sigue activo: lo mantiene `0x4375e74c` mientras el modo `[0x43f68c92]` valga `0x200` (solo `0x207/0x245/0x258/0x209/0x247` lo liberan)."""
    import struct

    pytest.importorskip("unicorn")
    L = pytest.importorskip("liro_vm")
    vm = _corre(2)
    obj = 0x43EA03E8

    def pide(clave: int) -> list:
        vm.limite += 300
        d = struct.pack("<6I", 0, clave, 0, 0, 0, 0)
        p = vm.malloc(0x60 + 12) + 12
        vm.uc.mem_write(p - 12, b"\0" * 8 + struct.pack("<I", 0x3040D7))
        vm.uc.mem_write(p, d)
        vm.msz[p] = len(d)
        s0 = len(vm.salida_ext)
        L.entrega(vm, 0x4015E, p)
        L.planifica(vm, 20_000_000)
        vm.limite += 500
        L.planifica(vm, 20_000_000)
        return vm.salida_ext[s0:]

    assert vm.rd(obj + 4) & 0x0400_0040 == 0  # factores 6 y 26 activos
    for clave in (0x1000, 0x1001, 0x1002):
        r = pide(clave)
        assert r and r[0][3] == 0x3040D7 and bytes.fromhex(r[0][4])[4:8] == struct.pack("<I", clave)
    assert vm.rd(obj + 4) & 0x0400_0000 == 0
    pide(0x1003)
    assert vm.rd(obj + 4) & 0x0400_0000  # factor 26 liberado
    assert vm.rd(obj + 4) & 0x40 == 0  # el 6 sigue activo
    assert vm.rd(0x43F68C92, 2) == 0x200


def _master(rol: int) -> tuple:
    """T13: tras EE_START entrega a `[CLK_CTRL]` (cola `0xc001bd`) el mensaje «from Master» (etiqueta `0x80c001bd`, `targetVfc=0`); `rol` = byte `[0x43e4a5a4]` que exige `0x435a0596` (DIAGNÓSTICO: nadie lo pone en la VM)."""
    import struct
    L = pytest.importorskip("liro_vm")
    vm = _corre()
    n0 = len(vm.log)
    vm.wr(0x43E4A5A4, rol, 1)
    d = struct.pack("<3I", 0, 1, 0)
    p = vm.malloc(0x60) + 12
    vm.uc.mem_write(p - 12, struct.pack("<3I", 0, 1, 0x80C001BD))
    vm.uc.mem_write(p, d)
    vm.msz[p] = len(d)
    vm.limite += 100
    L.entrega(vm, 0xC001BD, p)
    for _ in range(6):
        vm.limite += 1000
        L.planifica(vm, 50_000_000)
    return vm, vm.log[n0:]


def test_master_de_clkctrl_no_hace_falta_para_el_modulo_0() -> None:
    """E2E-3 (T13 DIAGNÓSTICO, corregido en T14): el receptor `0x435a0596` solo da por válido el «from Master» (etiqueta `0x80c001bd`) si el byte `[0x43e4a5a4]`==2; en el volcado real
    ese byte vale 0 (cámara en reposo). Con `Backup_read_multi` el módulo 0 ya está en 0x105 sin Master, y forzarlo no mueve nada: el guion sigue en la barrera 12 por el bloque del módulo 3."""
    vm0, log0 = _master(0)
    assert any("unknown message" in x for x in log0) and vm0.rd(0x43E9BD58, 2) == 0x105
    vm, log = _master(2)
    assert any("Receive Message from Master src=0x80c001bd" in x for x in log)
    assert [vm.rd(a, 2) for a in (0x43E9BD58, 0x43EC7ADC, 0x43E9C7D8)] == [0x105, 0x285, 0]
    assert vm.rd(0x43EDE340 + 0x18) == 12


def test_idt_cam_de_nflasha3_es_el_de_la_ram_real_y_quita_init_ng() -> None:
    """E2E-10 (T14, VERIFICADO): `SABIN/IDT_CAM.BIN` del `nflasha3` 3.21 está byte a byte en `0x83501000` del volcado real `ram-servicio-20261020` (u16 0x3d en la cabecera, lo que
    exige `0x439fd508`); cargado ahí, av-cam deja de registrar «IDT : Init NG»."""
    F = pytest.importorskip("avcam_fuente")
    nf = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3"
    if not nf.exists():
        pytest.skip("falta nflasha3 de fábrica")
    idt = F.idt_de(nf)
    assert idt[:2] == b"\x3d\x00"
    ram = ROOT / "analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin"
    if ram.exists():
        with ram.open("rb") as f:
            f.seek(0x83501000 - 0x80000000)
            assert f.read(len(idt)) == idt
    vm = _corre()
    assert not any("IDT : Init NG" in x for x in vm.log)
