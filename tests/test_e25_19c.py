"""E25-19c: emisor del mensaje (3,3) y cronómetro `cap+0x728`, desde bytes de av-cam.bin y capturas guardadas."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import e25_19b_dis as dis
import e25_19c_emisor as em
import e25_19c_temporizador as tm

EV = ROOT / "analysis" / "e25-19c"
needs_bin = pytest.mark.skipif(not dis.BIN.exists(), reason="av-cam.bin no disponible")


def test_tv_roundtrip():
    assert em.tv_a_segundos(3584) == pytest.approx(4.0)
    assert em.tv_a_segundos(0x1600) == pytest.approx(1 / 64)


def test_pkt_0c_vivo():
    r = json.loads((EV / "emisor-vivo.json").read_text())
    assert r["rx_var_0x43e77284"] == r["tx_var_0x43ed4cb0"]  # misma cola: receptor Darwin y caif_recv
    assert r["pkt_0c"]["tv"] == 3243 and r["pkt_0c"]["t_s"] == pytest.approx(10.07, abs=0.01)


def test_temporizador_coherente_con_tv():
    for c in tm.analiza().values():
        assert c["t_tv_s"] == pytest.approx(c["ticks_x32us_s"], rel=0.003)
    assert tm.analiza()["8s"]["tv_inferido"] == 3243  # coincide con pkt[2..3] leído


def _ins(addr: int, n: int) -> str:
    return "\n".join(dis.dis(dis.BIN.read_bytes(), addr, n))


@needs_bin
def test_ticks_son_us_entre_32():
    t = _ins(0x438C8AD0, 0x14)
    assert "bl #0x43840f7c" in t and "lsrs r0, r0, #5" in t and "str.w r5, [r4, #0x728]" in t


@needs_bin
def test_rama_mensaje_arma_cronometro_sin_plazo():
    assert "mov.w r5, #-1" in _ins(0x438C8AFE, 4)  # 74f != 0: plazo -1
    assert "bl #0x43b1f1ec" in _ins(0x438C8B18, 4)


@needs_bin
def test_sub10_lee_cronometro():
    assert "bl #0x43b1e492" in _ins(0x43B1E8CA, 4)
    assert "str.w r3, [r4, #0x728]" in _ins(0x43B1E4B4, 4)


@needs_bin
def test_receptor_0e_publica_en_buzon():
    assert "bl #0x4356120c" in _ins(0x436B8F1E, 4)
    assert "cmp r6, r2" in _ins(0x437DBA92, 2)  # caif_recv compara la subclase esperada (3)
