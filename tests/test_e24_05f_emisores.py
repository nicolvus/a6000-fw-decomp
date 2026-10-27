"""E24-05f: emisores mss de Darwin de los ocho mensajes Darwin→BIONZ (bytes de `darwin_core.bin`).
Informe: docs/capture/e24-05f-emisores-mss-darwin.md. Verifican instrucciones, tablas y referencias, no el texto del informe.
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e24_05f"))
sys.path.insert(0, str(ROOT / "scripts/e24_05"))

from dwn import DARWIN

if not DARWIN.exists():
    pytest.skip("falta darwin_core.bin", allow_module_level=True)

import emisores as e


@pytest.fixture(scope="module")
def res():
    return json.loads(json.dumps(e.main(), default=str))


def sites(res, api):
    return {(int(s["site"], 16)): (s["idx"], s["id"], s["dir"]) for s in res["send_sites"] if s["api"] == api}


def test_binary_is_the_expected_one(res):
    assert res["sha256"] == "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"


def test_mss_table_lengths_of_the_eight_tx_ids(res):
    t = res["mss_table"]
    want = {0x0B: 7, 0x0D: 75, 0x0E: 2, 0x10: 336, 0x11: 16, 0x14: 2, 0x15: 2, 0x17: 6}
    for i, n in want.items():
        assert t[hex(i)]["dir"] == "Darwin→BIONZ" and t[hex(i)]["len"] == n


def test_index_to_id_tables(res):
    assert res["id_tables"]["A"][:9] == ["0xb", "0xd", "0x15", "0xe", "0x10", "0x10", "0xc", "0x16", "0xf"]
    assert res["id_tables"]["B"][:4] == ["0x11", "0x14", "0x12", "0x13"]


def test_every_send_site_maps_a_constant_index_to_the_expected_id(res):
    a, b = sites(res, "A"), sites(res, "B")
    assert a[0x17142] == (0, "0xb", "TX") and a[0x172C4] == (1, "0xd", "TX") and a[0x17308] == (2, "0x15", "TX")
    assert a[0x17428] == (3, "0xe", "TX") and a[0x17530] == (5, "0x10", "TX")
    assert {a[0x17172][1], a[0x17340][1], a[0x17458][1]} == {"0xc", "0x16", "0xf"} and a[0x17172][2] == "RX"
    assert b[0x21284] == (0, "0x11", "TX") and b[0x212AA] == (1, "0x14", "TX")
    assert {b[0x212D0][1], b[0x212F6][1]} == {"0x12", "0x13"}


def test_message_fsm_roles_build_then_send(res):
    r = res["fsm_a_roles"]
    assert r["0"] == ["BUILD(0)"] and r["1"] == ["SEND(0)"] and r["2"] == ["SEND(6)"] and r["3"] == ["RECV(6)"]
    assert r["7"] == ["BUILD(1)"] and r["8"] == ["SEND(1)"] and r["9"] == ["BUILD(2)"] and r["10"] == ["SEND(2)"]
    assert r["15"] == ["BUILD(3)"] and r["16"] == ["SEND(3)"]
    assert r["22"] == ["BUILD(4)"] and r["23"] == ["BUILD(5)"] and r["24"] == ["SEND(5)"]


def test_builders_cover_indexes_0_to_5(res):
    b = res["builder_cases"]
    assert set(b) == {str(k) for k in range(6)}
    assert b["4"]["calls"] == ["0x1eda2"] and b["5"]["calls"] == ["0x1ed72"]  # 0x10 (336 B) se construye en dos partes


def _op(res, key, entry):
    return next(o for o in res[key] if o["entry"] == entry)


def test_admission_sends_0x0b_then_waits_0x0c(res):
    o1, o2 = _op(res, "fsm_a_ops", "0x16c64"), _op(res, "fsm_a_ops", "0x16c82")
    assert o1["seq"] == [0, 1, 47, 50] and o1["callers"] == ["0x17f9e"]
    assert o2["seq"] == [2, 47, 3, 50] and o2["callers"] == ["0x17faa"]
    assert res["admission_prefix_calls"][:3] == ["0x1e5b4", "0x17e94", "0x16c64"]  # sin llamadas a motor ni compuerta


def test_0x0d_0x15_sent_by_capture_states_9_and_11(res):
    full = [0x4, 5, 6, 7, 8, 47, 9, 10, 47, 11, 47, 12, 50]
    assert _op(res, "fsm_a_ops", "0x16ca4")["seq"] == full and _op(res, "fsm_a_ops", "0x16ca4")["capture_states"] == [9]
    assert _op(res, "fsm_a_ops", "0x16cd8")["capture_states"] == [9]
    short = _op(res, "fsm_a_ops", "0x16d2e")
    assert short["seq"] == full[3:] and short["capture_states"] == [11]


def test_0x0e_0x10_sent_by_fsm_c_state_5_run_from_capture_state_31(res):
    run = _op(res, "fsm_c_ops", "0x1e6ba")
    assert run["seq"] == [13, 5, 2, 3, 10, 4, 6, 9, 15] and run["capture_states"] == [31]
    op = _op(res, "fsm_a_ops", "0x16e92")
    assert op["callers"] == ["0x1ea62"] and res["fsm_c_state5"] == "0x1ea5c"
    assert 16 in op["seq"] and 24 in op["seq"]  # SEND 0x0e y SEND 0x10
    assert [s for s in op["seq"] if s in (15, 22, 23)] == [15, 22, 23]  # 0x0e antes que 0x10


def test_every_capture_list_contains_a_sender_and_state_31(res):
    for lst in res["capture_order"].values():
        assert (lst["pos_9"] is None) != (lst["pos_11"] is None)  # un solo emisor de 0x0d/0x15 por lista
        assert lst["pos_31"] is not None
        sender, starter = lst["pos_9"] if lst["pos_9"] is not None else lst["pos_11"], lst["pos_4"] if lst["pos_4"] is not None else lst["pos_5"]
        assert sender < starter < lst["pos_31"]  # 0x0d/0x15 salen antes de la máquina exterior; 0x0e/0x10 después


def test_outer_starters_live_in_capture_states_4_and_31_not_in_sender_states(res):
    s = res["outer_starter_states"]
    assert s["0x19998"] == [4] and {5, 31} <= set(s["0x199b8"]) and not {9, 11} & set(s["0x19998"] + s["0x199b8"])


def test_sender_code_does_not_reach_gate_motor_or_outer_starters(res):
    assert res["gate_hits_in_sender_closure"] == {}


def test_fsm_d_sends_0x11_0x14_only_for_modes_0_to_8(res):
    modes = {m["key"]: m["seq"] for m in res["fsm_d_modes"]}
    for k in range(9):
        assert 0 in modes[k] and 2 in modes[k] and modes[k].index(0) < modes[k].index(2)
    assert 0 not in modes[9] and 2 not in modes[9] and 0 not in modes[10] and 2 not in modes[10]


def test_fsm_d_starters_have_no_direct_callers(res):
    # 0x1a3ec solo se alcanza por el puente 0x17cea y 0x1aa28 por 0x19c4c <- 0x1c0b6 (tabla de eventos): disparo no resuelto
    assert any(k == "0x1c0b7" for _, k in res["event_table_0x295c8"])


def test_0x17_is_emitted_by_the_mode_switch_handler(res):
    assert res["mode_switch_emit17"] == ["0x1274a"] and res["mode_switch_caller"] == ["0x7c68"]
    assert "0x1fe66" not in res["mode_switch_closure_hits"]


def test_0x0b_byte0_is_the_decoded_busy_class():
    # S+0x43 (decodificación de la máscara de ocupación, 0x17e94) -> 0x1828e -> byte 0 del búfer del 0x0b (caso 0 del constructor)
    import capture_flow as cf
    from dwn import Core
    c = Core()
    assert cf.busy_bit_decode(c)[24] == 0x16  # el bit 24 (rearme sin terminar) se decodifica como código 0x16
    body = [(i.mnemonic, i.op_str) for i in c.dis(0x1828E, 0x1C)]
    assert ("cmp", "r0, #0xfe") in body and ("cmp", "r0, #0x10") in body and ("movs", "r0, #2") in body
    case0 = [(i.mnemonic, i.op_str, i.address) for i in c.dis(0x1EE14, 12)]
    assert case0[0][:2] == ("bl", "#0x1828e") and case0[1][:2] == ("strb", "r0, [r4]")
    pre = [(i.mnemonic, i.op_str) for i in c.dis(0x17F8C, 0x2A)]
    assert ("bl", "#0x17e94") in pre and ("strb.w", "r0, [r4, #0x43]") in pre  # S+0x43 se fija antes de enviar el 0x0b
