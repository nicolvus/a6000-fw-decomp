"""E24-05h-3: máquina ADC-B, su terminación con `0x20c74=0`, temporizadores y configuración de P29.
Verifican bytes/instrucciones/tablas reales. Informe: docs/capture/e24-05h-3-adcb-p29.md
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
for d in ("e24_05h3", "e24_05h", "e24_05g", "e24_05f", "e24_05", "e24_05d"):
    sys.path.insert(0, str(ROOT / "scripts" / d))

from dwn import DARWIN

if not DARWIN.exists():
    pytest.skip("falta darwin_core.bin", allow_module_level=True)

import adcb_p29 as a


@pytest.fixture(scope="module")
def res():
    return json.loads(json.dumps(a.main(), default=str))


def allok(d):
    return all(allok(v) if isinstance(v, dict) else v is True for v in d.values())


def test_descriptor_adcb(res):
    d = res["descriptores"]["ADC-B"]
    assert (d["tabla"], d["terminal"], d["timers_id"]) == ("0x29ee0", 7, [9, 13, 13])
    assert list(d["estados"]) == [str(i) for i in range(8)]  # 0..6 + centinela terminal 7
    assert all(res["ptrs_ADC-B_en_S"][k] for k in ("pos", "id", "celda"))


def test_listas_instaladas_en_adcb(res):
    got = {i["funcion"]: i["lista"] for i in res["instalaciones_ADC-B"]}
    assert got == {"0x2041e": [1, 4, 6, 7], "0x2027c": [1, 5, 6, 7], "0x202f2": [1, 3, 6, 2, 7]}


def test_unicos_escritores_y_reinicios(res):
    assert {s["funcion"] for s in res["forzar_terminal_ADC-B"]} == {"0x201d0", "0x206ec"}
    assert res["reinicios_ADC-B"] == [] and res["saltos_ADC-B"] == []
    assert res["ptrs_ADC-B_en_S"]["literales_de_la_direccion"] == {"0x2000381e": ["0x29dd0"], "0x2000381f": ["0x29dd4"], "0x20003820": ["0x29dd8"]}


def test_forzado_a_terminal_por_inicializacion_y_aborto(res):
    c = res["cadena_forzar_terminal"]
    assert c["0x201d0"] == ["0x197fe"] and c["0x197f8"] == ["0xcec8"] and c["0x206ec"] == ["0x19b8e"] and c["0x19b6e"] == ["0xcefa"] and c["0x19b8e_salto_a_0x206ec"]


def test_motor_y_predicado_hecho(res):
    assert allok(res["motor"])


def test_manejadores_adcb_sin_fail_salto_ni_bucles(res):
    for sid, h in res["manejadores_ADC-B"].items():
        assert not h["FAIL_en_cierre"] and not h["SALTO_en_cierre"] and not h["bucles_internos"], sid
    assert [s for s, h in res["manejadores_ADC-B"].items() if h["usa_0x1fe66"]] == ["4"]
    assert not any(h["lecturas_pin_0x51c6"] for h in res["manejadores_ADC-B"].values())
    arma = [s for s, h in res["manejadores_ADC-B"].items() if h["arma_temporizador"]]
    assert arma == ["1"]
    assert all(h["hecho"] for s, h in res["manejadores_ADC-B"].items() if s != "1")


def test_simulacion_alcanza_el_terminal_con_una_sola_espera(res):
    for rows in res["simulacion"].values():
        assert rows[-1]["siguiente"] == 7
        assert [r["espera"] is not None for r in rows].count(True) == 1 and rows[0]["estado"] == 1


def test_arrancadores_y_ramas(res):
    assert allok(res["arrancadores"]["0x2041e"]) and allok(res["arrancadores"]["0x202f2"]) and allok(res["arrancadores"]["0x2027c"])


def test_compuerta_no_depende_del_tipo_de_bobina(res):
    g = res["compuerta_0x19b9e"]
    assert allok(g["bytes"]) and g["llama_a_0x20c74"] is False and g["cierre"] == ["0x165c8", "0x19b9e"]
    assert g["escribe_S444"] == ["0x16558"] and g["escribe_S170"] == ["0x197f8", "0x19b6e"]
    assert allok(res["gate_0x201b0"])


def test_tipo0_solo_suprime_p4d_p4e(res):
    sc = res["escenarios_por_estado"]
    for sid, v in sc.items():
        assert set(v["tipo0"]) <= set(v["tipo≠0"]), sid
        assert "P4E" not in v["tipo0"] and "P4D" not in v["tipo0"] and v["FAIL"] is False
    assert "P4E" in sc["4"]["tipo≠0"] and "P4D" in sc["5"]["tipo≠0"] and sc["5"]["tipo0"] == {}


def test_cadena_del_ejecutor_y_evento_del_temporizador(res):
    c = res["cadena_ejecutor"]
    assert allok(c["bytes"]) and c["tabla_0x296d4"]["[0]"] == "0x1d04d" and c["llamadores"]["0x197c6"] == ["0x1d060"]
    t = res["temporizadores"]
    assert allok(t["bytes"]) and (t["id_timer0_ADC-B"], t["indice_bloque_B"], t["canal_hw"]) == (9, 1, 0)
    assert t["perifericos"]["palabra_config_0x2796c"] == "0x10400" and allok(t["93e6"]["chk"])


def test_conversion_s32_a_microsegundos(res):
    t = res["tiempo"]
    assert (t["exposicion_us(0x1600)"], t["exposicion_us(0x1400)"], t["exposicion_us(0x1000)"]) == (15625, 62500, 1_000_000)
    assert allok(t["bytes_0x19a12"]) and t["factor_literal_1e6"]


def test_estado31_variante_s32_distinto_de_cero(res):
    e = res["estado31_S32_no_cero"]
    assert all(v for k, v in e.items() if k.startswith("0x") and isinstance(v, bool))
    assert e["llamadas_a_0x203ae_en_0x18d6e"] == ["0x18e8a", "0x18f7e", "0x18f88"]


def test_p29_tabla_int_y_lectores(res):
    p = res["p29"]
    assert p["tabla_0x2675c"] == [{"pin": "0x124", "clave": "0x29", "INT": 5, "alt": 0, "alias": "0x4266c328"}]
    assert p["escritores_directos_P29"] == ["0x1ec9c", "0x7c8a"] and p["llamador_0x5512"] == ["0x5658"]
    assert allok(p["inicializacion_0x5512"])


def test_p29_modos_y_grupos(res):
    p = res["p29"]
    assert p["modos_tbb"]["bytes"] == "4506273845333d4147454f54" and p["modos_tbb"]["destinos"]["5"] == "0x5654"
    assert allok(p["volcado_a_hw"]) and allok(p["semantica_modo1"]) and allok(p["semantica_modo2"]) and allok(p["semantica_modo5"])
    modo = {g: v["P29"][0]["modo"] for g, v in p["grupos"].items()}
    assert modo == {"0": 1, "1": 1, "2": 2, "3": 5, "4": 2, "5": 1, "6": 1} and p["pull_en_P29"]
    assert all(v["P4E_salida_modo1"] for v in p["grupos"].values())
    assert p["tablas_secundarias_0x5b60"]["entradas_puerto2_bit9"] == []


def test_p29_arranque_y_cambios_posteriores(res):
    p = res["p29"]
    assert allok(p["arranque"]) and p["llamadas_5792"]["0x478a"]["r0_inmediatos"] == [0, 1]
    assert len(p["llamadas_5792"]) == 10
