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


def _puente(salida: list[bytes]):
    p = pytest.importorskip("puente")
    if not p.L.AVCAM.exists() or not p.L.LIRO_KO.exists():
        pytest.skip("faltan av-cam.bin o liro.ko (no versionados)")
    return p.Puente(salida.append)


def test_av_cam_responde_peticion_dataflow() -> None:
    salida: list[bytes] = []
    pu = _puente(salida)
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
