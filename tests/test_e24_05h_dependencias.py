"""E24-05h: P29, escrituras a P4E, productor BIONZ del 0x0c, modos Darwin y semántica de FAIL.
Verifican bytes/instrucciones/ramas reales, no el texto del informe. Informe: docs/capture/e24-05h-dependencias-finales-captura.md
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
for d in ("e24_05h", "e24_05g", "e24_05f", "e24_05", "e24_05d"):
    sys.path.insert(0, str(ROOT / "scripts" / d))

from dwn import DARWIN

if not DARWIN.exists():
    pytest.skip("falta darwin_core.bin", allow_module_level=True)

import dependencias_finales as d


@pytest.fixture(scope="module")
def res():
    return json.loads(json.dumps(d.main(), default=str))


def test_p29_es_pdir2_bit9_y_solo_dos_lectores_directos(res):
    assert res["p29"]["pin"] == "P29"
    assert res["p29"]["inmediato_0x124_en"] == ["0x1ec9c", "0x7c8a"]


def test_wrappers_de_p29_devuelven_1_si_y_solo_si_el_nivel_es_bajo(res):
    # 0x16c44: cbz r0 -> movs r0,#1 | movs r0,#0 ; 0x16c54: movs r4,#0; cbnz r0 -> (omite movs r4,#1)
    assert res["p29"]["bytes_wrappers"]["0x16c44"]["bytes"] == "10b508f029f808b1002010bd012010bd"
    assert res["p29"]["bytes_wrappers"]["0x16c54"]["bytes"] == "10b5002408f020f800b90124204610bd"


def test_espera_estado31_con_s32_cero_solo_sale_por_p29(res):
    assert res["salidas_espera_P29_0x18fa0"] == ["0x19062->0x190da"]
    assert res["p29"]["lectores"]["0x16c44"] == ["0x18fa0"]


def test_espera_estado31_con_s32_distinto_de_cero_sale_por_la_fsm_adc_b_no_por_p29(res):
    assert "0x18f86->0x18f90" in res["salidas_espera_ADC_B_0x18d6e"]
    assert "0x18d6e" in res["p29"]["lectores"]["0x16c54"][-1:] or "0x18d6e" in res["p29"]["lectores"]["0x16c54"]


def test_umbrales_de_la_espera_de_p29(res):
    u = res["p29"]["umbrales_0x18fa0"]
    assert sorted(u.values()) == [5000, 25000, 50000, 250000, 500000]


def test_p4e_solo_se_escribe_con_tipo_de_bobina_distinto_de_cero(res):
    for k, v in res["p4e"].items():
        if k.startswith("0x2"):
            assert "P4E" not in v["tipo0"], k
            assert "P4D" not in v["tipo0"], k
    assert "P4E" in res["p4e"]["0x20d00 (P4E=1)"]["tipoN"]


def test_con_tipo0_la_unica_salida_cortina_es_p4c_a_cero(res):
    for name in ("0x20d26 (paso -n)", "0x20e0e (paso 0)", "0x20e98 (paso +n)"):
        w = res["p4e"][name]["tipo0"]
        assert set(w) == {"P4C"}
        assert all(r1 == 0 for _, r1 in w["P4C"])


def test_no_hay_otro_inmediato_ni_literal_0x238(res):
    assert res["p4e"]["inmediatos_0x238"] == ["0x20ce4", "0x20d10", "0x20d4c", "0x20e6a", "0x20ec0", "0x20f70"]
    assert res["p4e"]["literales_0x238"] == []
    assert res["p4e"]["callers_pdor_rmw_0x51f2"] == ["0x20e3e"]


@pytest.mark.parametrize("raiz", ["estado31_espera_P29 (S+0x32=0)", "estado31_espera_ADC-B (S+0x32!=0)", "estado31_entrada"])
def test_cierre_del_estado31_con_tipo0_no_escribe_p4d_ni_p4e(res, raiz):
    c = res["cierres"][raiz]
    assert "P4E" in c["pines"] and "P4D" in c["pines"]  # con tipo != 0 sí
    assert "P4E" not in c["pines_tipo0"] and "P4D" not in c["pines_tipo0"]
    assert c["genericos_sin_resolver"] == []


def test_modos_0_1_2_no_escriben_bobinas_ni_motor(res):
    for m in ("modo0", "modo1", "modo2"):
        p = res["cierres"][m]["pines"]
        assert not {"P4C", "P4D", "P4E", "P40", "P41"} & set(p), m


def test_modo2_alcanza_la_fsm_adc_a_pero_con_tipo0_sus_manejadores_no_tocan_bobinas(res):
    assert any(x.startswith("ADC-A") for x in res["cierres"]["modo2"]["arrancadores_fsm"])
    a = res["fsm_adc"]["ADC-A"]
    assert {"P4D", "P4E"} <= set(a["pines_tipoN"]) and not {"P4C", "P4D", "P4E"} & set(a["pines_tipo0"])


def test_p4c_se_fija_a_1_en_cada_toma_independientemente_del_tipo(res):
    assert "0x17cee" in res["p4c_se_fija_a_1_en"]


def test_fail_no_avanza_el_estado_y_hecho_continua_el_bucle(res):
    m = res["motor_fsm"]
    assert m["0x1e4c2_fija_0x80"] and m["0x1e4aa_fija_0x40"] and m["fail_salta_avance"]
    assert m["avance_posicion"] and m["hecho_devuelve_1"] and m["bucle_continua_si_ret"]
    assert m["estado26_cae_a_fail"] and m["exterior_ids_con_FAIL"] == []


def test_estados_interiores_con_fail_incluyen_el_26(res):
    assert 26 in res["motor_fsm"]["estados_con_FAIL_directo"]


def test_constructor_bionz_del_0x0c_escribe_siete_campos(res):
    b = res["bionz"]
    assert b["campos_escritos_payload+"] == ["0x40", "0x47", "0x48", "0x4c", "0x4d", "0x4e", "0x52"]
    assert b["llamantes"] == ["0x438d034a", "0x438d042c"]


def test_tipo_bionz_de_darwin_sale_del_estado_bionz_con_tbb(res):
    g = res["bionz"]["tbb_estado_bionz_a_destino"]
    assert g["0x438d00ce"] == [7] and g["0x438d00ca"] == [8, 20, 27] and g["0x438d00fc"] == [5, 9, 19, 24, 31, 32]


def test_darwin_no_copia_pkt_0xc_a_s_0x3c_en_0x17f8c(res):
    c = res["darwin_copia_0x0c"]
    assert "pkt[0x2]->S+0x32" in c and "pkt[0xd]->S+0x3d" in c
    assert not any(x.endswith("S+0x3c") for x in c)
