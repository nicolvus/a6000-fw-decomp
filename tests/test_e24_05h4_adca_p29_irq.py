"""E24-05h-4: ADC-A invocada por ADC-B, grupo activo de P29 y cadena de entrega del evento de ADC-B.
Verifican bytes/instrucciones/tablas reales. Informe: docs/capture/e24-05h-4-adca-p29-irq.md
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
for d in ("e24_05h4", "e24_05h3", "e24_05h", "e24_05g", "e24_05f", "e24_05", "e24_05d"):
    sys.path.insert(0, str(ROOT / "scripts" / d))

from dwn import DARWIN

if not DARWIN.exists():
    pytest.skip("falta darwin_core.bin", allow_module_level=True)

import adca_p29_irq as m


@pytest.fixture(scope="module")
def res():
    return json.loads(json.dumps(m.main(), default=str))


def checks(d):
    """Todas las comprobaciones booleanas de bytes anidadas en `d`."""
    for k, v in d.items():
        if isinstance(v, bool) and k.startswith("0x"):
            yield v
        elif isinstance(v, dict):
            yield from checks(v)


def test_lista_de_adca_desde_adcb(res):
    a = res["A_ADC-A"]
    assert a["lista_desde_ADC-B"] == [2, 4, 6, 16, 17]
    assert all(a["estado4_ADC-B"].values())
    assert {i["sitio"] for i in a["instalaciones_ADC-A"] if i["lista"] == [2, 4, 6, 16, 17]} == {"0x2045c", "0x205d0", "0x20ae0"}
    assert "0x20ae6" in {s["sitio"] for s in a["ejecuciones_idx0"]}


def test_contexto_del_motor_es_de_pila(res):
    a = res["A_ADC-A"]
    assert all(a["ctx_en_pila"].values()) and all(a["ejecutor_0x20c06"].values())


def test_adca_tipo0_sin_ciclos_pines_ni_indirectos(res):
    fl = res["A_ADC-A"]["flujos_por_estado"]
    assert set(fl) == {"2", "4", "6", "16"}
    for v in fl.values():
        t0 = v["tipo0"]
        assert (t0["ciclos"], t0["indirectos"], t0["lee_pin_0x51c6"]) == ({}, [], False)
        assert t0["funciones"] <= 6


def test_adca_tipoN_solo_agrega_cierre(res):
    fl = res["A_ADC-A"]["flujos_por_estado"]
    assert "0x210a2" in fl["2"]["solo_tipoN"] and "0x16ff4" in fl["4"]["solo_tipoN"]
    assert fl["2"]["tipoN"]["ciclos"] and not fl["2"]["tipo0"]["ciclos"]


def test_simulacion_adca(res):
    rows = res["A_ADC-A"]["simulacion_ADC-A"]
    assert [(r["invocacion"], r["estado"], r["hecho"], r["temporizador"]) for r in rows] == [(0, 2, False, False), (1, 4, False, True), (2, 6, True, False), (2, 16, True, False)]
    assert rows[0]["siguiente"] == 4 and rows[-1]["siguiente"] == 17


def test_temporizador_de_adca_es_otro_hardware(res):
    t = res["A_ADC-A"]["temporizador"]
    assert (t["id"], t["canal_hw"], t["callback_0x2969c[11]"]) == (5, 11, "0x1d041")
    assert all(t["bytes"].values()) and all(t["cadena_evento"].values()) and all(t["otras_cuentas_ticks"].values())
    assert all(t["despacho_base_timer"]["bytes"].values()) and t["despacho_base_timer"]["vectores_0x43ac"] == ["0xf305", "0xf317", "0xf329", "0xf2d9"]


def test_cierres_de_adcb_sin_ciclos(res):
    cl = res["A_ADC-B_cierres_podados"]
    assert set(cl) == {str(i) for i in range(7)}
    for v in cl.values():
        for k in ("tipo0", "tipoN"):
            assert v[k]["ciclos"] == {} and not v[k]["lee_pin_0x51c6"]
        assert set(v["tipo0"]["indirectos"]) <= {"0x94e8 blx r1"}


def test_capture_exige_ambas_en_terminal(res):
    t = res["A_dependencia_terminal"]
    assert all(checks(t["estado_3"])) and all(checks(t["estado_32"])) and all(t["predicado_0x20c34"].values())
    assert t["estado_3"]["entrada_tabla"] == ["0x3", "0x1860d"] and t["estado_32"]["entrada_tabla"] == ["0x20", "0x192a1"]
    assert t["literal_0x20c42"] == "0x29d90"
    assert all(all(v.values()) for v in t["esperas_activas"].values())
    assert t["en_estado_31_0x18d6e"] == []
    lista = t["orden_lista_captura"]
    assert lista[lista.index(31) + 1] == 32


def test_grupos_por_estado(res):
    b = res["B_P29_grupo"]
    assert {k: v["grupos"] for k, v in b["grupos_por_estado"].items()} == {"Init": [5], "Seton": [2], "On": [3], "(3)": [4], "Off": [5], "Upd": []}
    assert len(b["llamadas_0x5792"]) == 10 and b["llamadas_0x5792"]["0x7618"] == {"funcion": "0x75f0", "grupo": 3}
    assert all(b["motor"].values()) and all(b["boot"].values())


def test_p29_en_grupo_3_es_int05(res):
    b = res["B_P29_grupo"]
    assert {k: v[0]["modo"] for k, v in b["grupos_P29"].items()} == {"0": 1, "1": 1, "2": 2, "3": 5, "4": 2, "5": 1, "6": 1}
    assert b["grupo3_P29"]["P29"][0] == {"modo": 5, "pull_bits": 0, "nivel_bits": 0, "mascara": "0x300"}
    assert all(b["lectores_P29_0x124"].values())


def test_captura_no_alcanza_cambiadores_de_grupo(res):
    b = res["B_P29_grupo"]
    assert b["raices_capture_fsm"] >= 150 and b["cierre_raices"] > 500
    assert b["interseccion_con_cambiadores_de_grupo"] == []


def test_on_solo_sale_por_mensaje_de_cola_0(res):
    b = res["B_P29_grupo"]
    assert all(b["On_main_0x76ce"].values()) and b["On_next_0x274b8"] == [3, 3]
    assert b["next_0x274a4"] == [1, 2, 3, 5] and b["next_0x274a8"] == [2, 3, 5, 3, 3]


def test_cadena_irq_de_adcb(res):
    c = res["C_irq_ADC-B"]
    assert all(checks(c["armado"])) and c["armado"]["bloqueB_id9"]["canal"] == 0
    assert all(c["callback_ADC-B"].values()) and all(checks(c["isr"]))
    assert all(checks(c["init_global"])) and all(checks(c["parada"]))
    assert c["isr"]["tabla_callbacks_0x2969c"] == {"[11]": "0x1d041", "[13]": "0x1d049", "[14]=0x296d4[0]": "0x1d04d", "[15]=0x296d8[1]": "0x1d065"}


def test_vectores_son_coherentes_con_irq_32_y_33(res):
    v = res["C_irq_ADC-B"]["isr"]["vectores_tabla_0x42fc"]
    assert (v["0x43bc"], v["0x43c0"], v["indice_IRQ_si_base_0x42fc"]) == ("0xf8d3", "0xfa95", [32, 33])
    assert v["tabla_0x4200_hasta_0x42ff_todas_por_defecto"] and v["reset_en_0x4300"] == "0x45c9"


def test_configuracion_del_canal_0(res):
    a = res["C_irq_ADC-B"]["armado"]
    assert (a["config_ch0_0x27970"], a["ctrl_0x1c_tras_0xf8ee_calculado"], a["config_global_0x2796c"]) == ("0x180", "0x2094", "0x10400")
