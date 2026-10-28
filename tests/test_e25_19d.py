"""E25-19d: escritores de `cap+0x74f` y rama de host de sub 9, ejecutados contra av-cam.bin."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e25_19d"))
import escritores_74f as barrido
import rama_host as rh
import tabla_escritores as tabla

pytestmark = pytest.mark.skipif(not rh.BIN.exists(), reason="av-cam.bin no disponible")


def test_solo_tres_escritores_de_74f():
    st = {x["addr"] for x in barrido.barrido(rh.BIN.read_bytes()) if x["ins"].startswith("strb") and x["ins"].endswith("0x74f]")}
    assert st == {0x438ACC9C, 0x437DF5E8, 0x438C2562}


def test_tabla_verificada_contra_bytes():
    r = tabla.verifica()
    assert len(r["escritores"]) == 3 and len(r["lectores"]) == 26


def test_ticks_reales_30s_sin_overflow():
    f = {x["caso"]: x for x in rh.tabla()}
    assert f["30 s"]["ticks"] == 937081 and f["30 s"]["ticks"] < 2**32
    assert f["4 s"]["ticks"] == 125001 and f["8 s"]["us"] == 8_000_000
    assert all(abs(x["error_rel"]) < 0.03 for x in f.values())  # los cortos pierden por cuantizar a 32 µs + 1 tick
    assert all(x["cb"] == "0x43b1e4c1" and x["cap728"] == x["ticks"] for x in f.values())


def test_tv_3243_son_10_07_s():
    assert rh.llama(rh.maquina(), 0x4382FAC8, 3243) == pytest.approx(10_070_000, rel=0.002)


def test_74f_o_740_distinto_de_host_arma_sin_plazo():
    o = rh.otras_ramas()
    assert o["74f=1"]["ticks"] == o["740=1"]["ticks"] == 0xFFFFFFFF
    assert o["74f=1"]["cb"] != 0x43B1E4C1
