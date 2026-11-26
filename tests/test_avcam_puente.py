"""Puente LIRO VM ↔ invitado (scripts/gui/avcam/puente.py): un mensaje dataflow de im.elf a una cola de av-cam recibe la respuesta real de av-cam."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))

# petición capturada en el arnés (13-11-2026): InfraAvbbcMsgManager → 0x5700f9, respuesta a 0x550120
REQ = ("5700f9", "28", "000000000000000020015500",
       "20015500a0a0a0a0010028001400000028000000001000001400020000000000020000000000000000000000")


def _puente(salida: list[bytes], request: pytest.FixtureRequest):
    p = pytest.importorskip("puente")
    if not p.L.AVCAM.exists() or not p.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    pu = p.Puente(salida.append)
    request.addfinalizer(pu.cierra)  # el hilo del reloj dentro de Unicorn aborta el proceso al cerrar el intérprete
    return pu


def test_av_cam_responde_peticion_dataflow(request: pytest.FixtureRequest) -> None:
    salida: list[bytes] = []
    pu = _puente(salida, request)
    pu.desde_invitado(" ".join(REQ))
    t0 = time.time()
    while not any(x.startswith(b"Q ") for x in salida) and time.time() - t0 < 3:
        time.sleep(0.05)
    qs = [x for x in salida if x.startswith(b"Q ")]  # (las líneas «H» llevan el encabezado del anillo)
    assert qs, "av-cam no respondió"
    q, cab, cuerpo = qs[0].decode().split()[1:]
    assert int(q, 16) == 0x550120                    # la cola de respuesta viaja en la petición (+0)
    assert cab.endswith("f9005700")                  # cabecera −1 = cola destino original: el receptor casa el remitente con ella
    assert cuerpo[8:16] == "a0a0a0a0" and cuerpo[40:48] == "00100080"   # dataflow: cate 0x1000, msg 0 ^ 0x8000


def test_no_reenvia_las_colas_de_entrada() -> None:
    p = pytest.importorskip("puente")
    assert 0x7A0020 in p.NO_REENVIAR  # las teclas las pone el anfitrión, no la LIRO VM


def test_colas_avcam_se_guardan_en_cache_por_contenido(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """live.py pedía las colas arrancando la LIRO VM entera (5–6 s) y el Puente la arrancaba otra vez: las colas son deterministas para el mismo
    av-cam, idt, bk.tbl y código de la VM, así que se calculan una vez por contenido y cambiar cualquiera de ellos las recalcula."""
    p = pytest.importorskip("puente")
    llamadas: list[Path | None] = []

    class Tarea:
        estado, espera = "espera", ("rcv", 0x4015E)

    class VmFalsa:
        qcb = {0x5A0048: None, 0x30001: None}
        tasks = {1: Tarea()}

    monkeypatch.setattr(p, "arranca", lambda avcam=None: (llamadas.append(avcam), (VmFalsa(), 0.0))[1])
    av = tmp_path / "av-cam.bin"
    av.write_bytes(b"uno")
    cache = tmp_path / "cache" / "colas.json"
    primera = p.colas_avcam(av, cache)
    assert primera == [0x30001, 0x4015E, 0x5A0048]
    assert p.colas_avcam(av, cache) == primera and len(llamadas) == 1  # segunda vez: de la caché, sin arrancar la VM
    av.write_bytes(b"dos")
    assert p.colas_avcam(av, cache) == primera and len(llamadas) == 2  # otro av-cam: se recalcula
    assert p.colas_avcam(av, None) == primera and len(llamadas) == 3  # sin caché: siempre se arranca


def test_vuelca_memoria_de_la_vm_bajo_demanda(request: pytest.FixtureRequest) -> None:
    """E2E-15: `/avmem?a=43ede338:4,...` (live.py) lee la memoria de la LIRO VM en vivo; sin esto no se ve en qué paso está el secuenciador."""
    pu = _puente([], request)
    r = pu.vuelca("43ede338:4,43e81240:8")
    assert set(r["mem"]) == {"43ede338", "43e81240"} and len(r["mem"]["43ede338"]) == 8 and len(r["mem"]["43e81240"]) == 16
    assert r["mem"]["43ede338"] == bytes(pu.vm.uc.mem_read(0x43EDE338, 4)).hex()
    assert pu.vuelca("10:4")["mem"]["10"] == "error"  # dirección no mapeada: no tumba el hilo


def test_escala_de_tiempo_ralentiza_la_vm_frente_al_reloj_real(request: pytest.FixtureRequest) -> None:
    """E2E-15: el invitado del arnés (TCG) tarda ≈20 s en mandar lo que la cámara manda en ≈2 s; sin escala la VM pasaba por sus plazos de arranque
    (módulo 1 `0x281` a 17 s) antes de la 1.ª orden y el secuenciador `[0x43ede338]` nunca salía de 0. Con `escala` el tiempo virtual avanza `escala` ms por ms real."""
    p = pytest.importorskip("puente")
    if not p.L.AVCAM.exists() or not p.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    pu = p.Puente(lambda _l: None, escala=0.25)
    request.addfinalizer(pu.cierra)
    t0 = pu.vm.limite
    time.sleep(1.0)
    assert 150 < pu.vm.limite - t0 < 400  # ≈250 ms virtuales por s real (sin escala: ≈1000)


def test_encabezado_del_anillo_se_comparte_con_el_invitado(request: pytest.FixtureRequest) -> None:
    """E2E-3 (T85): libObj mapea de /dev/mem el encabezado de 0x40 B del anillo de av-cam (0x82d90000) y escribe en él los índices ([4],[8],[c],[0x3c]);
    av-cam escribe el resto ([0]=0x100). Sin compartirlo, av-cam leía [hdr+8]=0, el factor 1 de RelLock seguía activo y S2 se rechazaba."""
    salida: list[bytes] = []
    pu = _puente(salida, request)
    hdr = 0x82D90000
    rd = lambda a: int.from_bytes(bytes(pu.vm.uc.mem_read(a, 4)), "little")  # noqa: E731
    with pu.cerrojo:
        pu.vm.uc.mem_write(hdr, (0x100).to_bytes(4, "little"))  # lo que av-cam escribe al abrir el anillo (≈7 s virtuales)
        pu._avanza()
    h = [s for s in salida if s.startswith(b"H ")]
    assert h and int.from_bytes(bytes.fromhex(h[-1][2:].decode())[:4], "little") == 0x100  # av-cam → invitado
    pu.cabecera_desde_invitado("ff ff ff 0")  # libObj → LIRO VM: reinicia los índices a 0xff
    assert (rd(hdr + 4), rd(hdr + 8), rd(hdr + 0xC), rd(hdr)) == (0xFF, 0xFF, 0xFF, 0x100)
    with pu.cerrojo:
        salida.clear()
        pu._avanza()
    assert all(not s.startswith(b"H ") or bytes.fromhex(s[2:].decode())[4:16] == bytes(12) for s in salida)  # los campos de libObj no vuelven al invitado


def test_el_puente_reutiliza_la_vm_que_arranco_colas_avcam(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G22-ARR2: con la caché de colas fría (cualquier cambio de scripts/gui/avcam/*.py o de av-cam/idt/bk.tbl/liro.ko) la LIRO VM
    arrancaba dos veces en el mismo inicio (colas + Puente); ahora `colas_avcam` entrega su VM al Puente y arranca una sola."""
    p = pytest.importorskip("puente")
    from types import SimpleNamespace
    from typing import ClassVar

    arranques: list[tuple] = []

    class VmFalsa:
        qcb: ClassVar[dict] = {0x30001: None}
        tasks: ClassVar[dict] = {}
        t = 5043.0
        sensor_v = SimpleNamespace(inicia=lambda _t: None)

    monkeypatch.setattr(p.L, "carga", lambda *a: (arranques.append(a), VmFalsa())[1])
    monkeypatch.setattr(p.L, "crea_tarea", lambda *_a: SimpleNamespace(estado="lista"))
    monkeypatch.setattr(p.L, "planifica", lambda *_a: None)
    av = tmp_path / "av-cam.bin"
    av.write_bytes(b"uno")
    cache = tmp_path / "colas.json"
    assert p.colas_avcam(av, cache) == [0x30001] and len(arranques) == 1
    vm = p.vm_de_colas(av)
    assert vm is not None and p.vm_de_colas(av) is None  # se entrega una sola vez
    vm2, t2 = p.arranca(av, vm=vm)  # lo que hace el Puente
    assert vm2 is vm and t2 == 5043.0 and len(arranques) == 1  # reutilizada: no se vuelve a cargar av-cam
    assert p.vm_de_colas(tmp_path / "otro.bin") is None  # otra imagen: no se reutiliza la de esta


def test_la_vm_de_colas_sirve_para_responder_la_peticion_dataflow(request: pytest.FixtureRequest, tmp_path: Path,
                                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """La VM que arranca `colas_avcam` es la misma que usaría el Puente recién arrancado: con ella responde la petición capturada y
    solo se carga av-cam una vez."""
    p = pytest.importorskip("puente")
    if not p.L.AVCAM.exists() or not p.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    real, montajes = p.L.carga, []

    def carga(*a):
        montajes.append(1)
        return real(*a)

    monkeypatch.setattr(p.L, "carga", carga)
    p.colas_avcam(None, tmp_path / "colas.json")  # caché fría: arranca la VM
    salida: list[bytes] = []
    pu = p.Puente(salida.append)  # reutiliza esa VM (si no, `montajes` tendría 2)
    request.addfinalizer(pu.cierra)
    pu.desde_invitado(" ".join(REQ))
    t0 = time.time()
    while not any(x.startswith(b"Q ") for x in salida) and time.time() - t0 < 3:
        time.sleep(0.05)
    assert [x for x in salida if x.startswith(b"Q ")]
    assert len(montajes) == 1
