"""Hallazgos estáticos S403 (E2, E3, E4, E5, E8, E12) y logger dual de S605–S627 (D3), contra los JSON generados."""
import json
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parents[1] / "analysis/s403_pendientes"
BIN = Path(__file__).resolve().parents[1] / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
                                             "nflasha3_unpacked_unpacked/av-cam.bin")


def load(name: str) -> dict:
    return json.loads((DIR / name).read_text())


def test_e2_check_only_rejects_id_3_or_null():
    e2 = load("static_findings.json")["E2"]
    assert e2["id_comparado"] == "0x10000003"
    assert e2["devuelve_1_para_la_fila"] is True  # la fila de estado usa 0x10000005


def test_e3_call_sites_and_writers():
    e3 = load("e3_params9.json")
    assert e3["sitios_de_llamada"] == ["0x438c79fc", "0x438c830c", "0x438c8824", "0x438cc894", "0x43ae937c"]
    assert e3["sitios_esperados_ok"] and e3["bloque_en_pila_ok"]
    assert {k: v["valor"] for k, v in e3["escritores_clasificados"].items()} == {
        "0x438c82bc": "0", "0x438c79e2": "4", "0x438c87f0": "1"}
    assert all(v["insn_ok"] for v in e3["escritores_clasificados"].values())
    assert e3["constantes_directas_en_sitios_de_llamada"] == [0, 1, 4]
    assert len(e3["escritores_anchos_en_0x654"]) == 14
    assert [w["addr"] for w in e3["escritores_strb_disp_0x655"]] == ["0x4389cc28", "0x438c79e2", "0x438c82bc", "0x438c87f0"]


def test_e4_mode_table_and_masks():
    e4 = load("static_findings.json")["E4"]
    assert e4["bytes_0_10"] == [0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0]
    assert e4["mascara_1"].endswith("#0x708") and e4["mascara_0"].endswith("#0xf3") and e4["limite"] == "cmp r1, #0xa"


def test_e5_bounded_absence():
    e5 = load("static_findings.json")["E5"]
    assert e5["a6000_anclas_a_G"] == 262
    assert [h["addr"] for h in e5["a6000_accesos_0x238"]] == ["0x438032dc"]  # solo el escritor del manejador 0x40e3
    assert e5["a7s_anclas_a_S"] == 73 and e5["a7s_stores_en_S0"] == []


def test_e7_slot_sites_only_read():
    e7 = load("static_findings.json")["E7"]
    assert e7["slot"] == "0x4401f990" and len(e7["sitios"]) == 14
    accesses = [a for site in e7["sitios"] for a in site["accesos"]]
    assert accesses and not any(a["insn"].startswith("str") for a in accesses)
    assert len({a["disp"] for a in accesses}) == 18


def test_e8_reader_chains_have_call_sites():
    e8 = load("static_findings.json")["E8"]
    for chain in e8.values():
        assert all(edge["sitios"] for edge in chain)


def test_e12_mailbox_has_only_sender_pools():
    e12 = load("static_findings.json")["E12"]
    assert len(e12["palabras_de_pool"]) == 13 and e12["movw_movt"] == 0
    assert e12["mensaje"] == {"len": 20, "tipo": 3, "sub": 34}


def test_d3_logger_dual_only_three_sheets_backed():
    sheets = load("d3_logger_dual.json")
    assert sorted(k for k, v in sheets.items() if v["estado"] == "VERIFICADO_ESTATICO") == ["S607", "S611", "S616"]
    assert sheets["S618"]["estado"] == "SIN_TRAZAS"
    others = [v for k, v in sheets.items() if v["estado"] == "NO_RESPALDADO_ESTATICO"]
    assert len(others) == 19 and all(v["con_ruta_global"] == 0 for v in others)
    assert sum(v["trazas"] for v in sheets.values()) == 94


@pytest.mark.skipif(not BIN.exists(), reason="firmware no presente")
def test_e3_instruction_bytes():
    import sys
    sys.path.insert(0, str(DIR))
    import e3_params9

    blob = BIN.read_bytes()
    assert e3_params9.text_at(blob, 0x438C87F0) == "strb.w sb, [r4, #0x655]"
    assert e3_params9.text_at(blob, 0x438C79E2) == "strb.w r3, [r4, #0x655]"


def test_d3_equivalence_homologues_are_not_identical():
    rows = load("d3_equivalence.json")
    compared = [r["modelos"]["a7s"]["mejor"] for r in rows if r["modelos"]["a7s"]["mejor"]]
    assert len(rows) == 17 and len(compared) == 10
    assert not any(c["root_igual_salvo_lineas"] for c in compared)  # instrucciones distintas: sin equivalencia de código
