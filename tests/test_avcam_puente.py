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
    while not salida and time.time() - t0 < 3:
        time.sleep(0.05)
    assert salida, "av-cam no respondió"
    q, cab, cuerpo = salida[0].decode().split()[1:]
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
