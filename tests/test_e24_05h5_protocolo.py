"""E24-05e / E24-05h-5: espacios de memoria de T022/T023 y productores BIONZ de pkt[1], pkt[2..3] (bytes de av-cam y texto de scripts).
Informe: docs/capture/e24-05e-05h5-protocolo-lectura.md
"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "e24_05h5"))
if not (ROOT / "analysis/rea-independent/input/av-cam.bin").exists():
    pytest.skip("falta av-cam.bin", allow_module_level=True)

import protocolo as m


@pytest.fixture(scope="module")
def res():
    return m.main()


def test_t022_t023_solo_leen_dram_de_bionz(res):
    e = res["A_espacios"]
    assert e["T022_T023"] == {**e["T022_T023"], "en_DRAM_BIONZ": True, "solape_SRAM_Darwin": False, "solape_perifericos_Darwin": False}
    assert e["T022_T023"]["ventana"] == ["0x83f91e20", "0x83f91f30"]
    assert all(int(x, 16) >= 0x83F91E20 for x in e["T022_T023"]["buffers"])


def test_ningun_script_de_camara_lee_direcciones_de_darwin(res):
    assert res["A_espacios"]["scripts_con_literales_0x20xxxxxx"] == []
    assert res["A_espacios"]["scripts_que_usan_dev_mem"]["camera_darwin_buffers.py"] == {"lee": True, "escribe": False, "fisicas": ["0x83f91e20", "0x83f91f24"]}


def test_el_script_es_offline():
    src = (ROOT / "scripts/e24_05h5/protocolo.py").read_text()
    assert not any(w in src for w in ("camera_telnet", "socket", "subprocess", "urllib"))


def test_instrucciones_del_constructor_y_filtro(res):
    assert all(res["B_paquete"]["bytes"].values())
    assert res["B_paquete"]["pkt_es_carga_mas_0x40"]


def test_globales_y_estructuras_de_pkt(res):
    p = res["B_paquete"]
    assert p["globales_pkt1"] == {"clase_0x43eedecc": "0x43eedecc", "flag_0x43f9b503": "0x43f9b503"}
    assert p["estructuras_sl"] == ["0x43f79f94", "0x43f7cac0"] and p["got"] == "0x4401eee4"
    assert p["sl_0x162_fisicas"] == ["0x83f7a0f6", "0x83f7cc22"]


def test_paquete_t022_coherente_con_el_constructor(res):
    t = res["B_paquete"]["T022"]
    assert (t["pkt1"], t["pkt23"], t["pkt45"], t["pkt_a_b"]) == (2, 0x1600, 0x13BD, 0x0E53)
    assert t["pkt23_supera_umbral_0xb00"] and t["pkt8"] == 0 and t["pkt8_inicial_0xa0_en_0x43841070"]


def test_tabla_de_direcciones(res):
    d = {x["nombre"]: x for x in res["C_direcciones"]}
    assert len(d) == 5 and all(int(x["fisica"], 16) == int(x["virt"], 16) + 0x40000000 for x in d.values())
    assert d["pkt 0x0c completo"]["fisica"] == "0x83f91e32" and d["pkt 0x0c completo"]["estado"].startswith("MEDIDO")
    assert all(x["via"] == "T022" for x in d.values())
