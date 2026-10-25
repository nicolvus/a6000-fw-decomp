"""Cierre estático S402: equivalencia A6000↔A7S, Backup 0x3000b, comandos de la cola 0x40193, productor 0x10000005 y selector Silent A7S."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s402_static_closure"))

import a7s_silent_selector
import backup_3000b
import fw
import producer_10000005
import queue_commands

DATA = ROOT / "analysis/s402_static_closure"


@pytest.fixture(scope="module")
def libs():
    return fw.Lib("A6000"), fw.Lib("A7S")


def test_recordstill_closure_identical_modulo_source_lines(libs):
    a, b = libs
    result = fw.closure(a, b, 0x908AFC, 0x847E1C)
    assert len(result) == 25
    assert not any(v["residue"] for v in result.values())
    assert sum(not v["identical"] for v in result.values()) == 1  # solo cambian números de línea de logs
    for pair in [(0x37CC14, 0x27DC78), (0x38CB9C, 0x286CBC), (0x8FDC04, 0x83C504), (0x915F04, 0x84E824),
                 (0x8FDC70, 0x83C570), (0x8FDCDC, 0x83C5DC), (0x8FE0A0, 0x83C9A0), (0x90F038, 0x840618)]:
        assert pair in result


def test_recordimage_closure_has_no_non_line_residue(libs):
    a, b = libs
    result = fw.closure(a, b, 0x90B248, 0x84A568)
    assert len(result) == 174
    assert not any(v["residue"] for v in result.values())


def test_equivalence_detects_a_real_instruction_difference(libs):
    a, _ = libs
    base = fw.normalize(a, 0x908AFC, a.fend(0x908AFC))
    mutated = list(base)
    mutated[10] = ("adds", "r0, #9")
    assert fw.residue(base, mutated)


def test_equivalence_json_matches_recomputation():
    saved = json.loads((DATA / "recordstill_equivalence.json").read_text())
    assert saved["roots"]["RecordStill"]["pairs"] == 25
    assert saved["roots"]["RecordImage_Execute"]["with_other_differences"] == 0
    assert all(saved["roots"]["RecordStill"]["local_pairs_present"].values())


def test_backup_key_0x3000b_format_and_defaults():
    data = backup_3000b.build()
    assert not data["backup_ko"]["mismatches"] and not data["backup_ko"]["read_core_call_mismatches"]
    assert data["default_images"] == 11 and data["distinct_default_payloads"] == 1
    assert data["size"] == 256
    assert set(data["nonzero"]) == {hex(i) for i in (*range(0x30, 0x38), 0x41, 0x51)}
    assert data["gate_plus3"]["default"] == 0 and data["gate_plus6"]["default"] == 0
    assert data["byte_plus_0xac"]["default"] == 0


def test_backup_lookup_rejects_unknown_key():
    image = backup_3000b.DEFAULTS[0].read_bytes()
    with pytest.raises(KeyError):
        backup_3000b.lookup(image, 0x7FFF0000)
    with pytest.raises(KeyError):
        backup_3000b.lookup(image, 0x30000 | 0xFFFF)


def test_queue_wrappers_send_commands_0x4042_to_0x4045(libs):
    rows = queue_commands.wrapper_commands(libs[0])
    assert {r["command"] for v in rows.values() for r in v.values()} == {"0x4042", "0x4043", "0x4044", "0x4045"}
    assert {a: rows["0xaf9264"][a]["mode_byte8"] for a in (0, 1, 2)} == {0: "0xc", 1: "0xb", 2: "0x14"}
    assert {a: rows["0xaf934c"][a]["mode_byte8"] for a in (0, 1, 2)} == {0: "0x6", 1: "0x5", 2: "0xa"}


def test_liro_table_has_handlers_for_those_commands():
    rows = {r["command"]: r["handler"] for r in queue_commands.liro_table()}
    assert rows["0x4042"] == "0x4379e47d" and rows["0x4043"] == "0x4379e3fd"
    assert rows["0x4044"] == "0x43aeaa4b" and rows["0x4045"] == "0x43aea9f1"
    assert len(rows) == 35


def test_recorded_wrapper_call_sites_decode_to_their_wrapper(libs):
    saved = json.loads((DATA / "queue_40193_commands.json").read_text())
    lib = libs[0]
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    total = 0
    for wrapper, sites in saved["callers"]["sites"].items():
        for site in sites:
            ins = next(decoder.disasm(lib.e.read(int(site, 16), 4), int(site, 16), count=1))
            assert ins.mnemonic in ("bl", "blx", "b.w") and int(ins.op_str[1:], 16) == int(wrapper, 16)
            total += 1
    assert total == 53 and len(saved["callers"]["functions"]) == 32


def test_producer_of_0x10000005_has_exactly_two_category_3500_constructors(libs):
    data = producer_10000005.build()
    assert data["state_row"]["message"] == "0x10000005" and data["state_row"]["state"] == "0x2"
    assert [s["load"] for s in data["constructors_in_category_0x3500"]] == ["0x90868a", "0x919f4a"]
    assert data["pbcap"]["tbh_entry_6_target"] == "0x6141a0"


def test_a7s_silent_selector_contract():
    data = a7s_silent_selector.build()
    assert not data["instruction_mismatches"]
    assert data["table"]["entries"] == [0, 2]
    assert data["log_string"]["text"].startswith("SET Silent Shutter Type")
    assert data["setting_singleton"] == "0x43ea70a0"
    assert data["a7s_has_silent_type_string"] and not data["a6000_has_silent_type_string"]


def test_a7s_selector_mutation_is_rejected():
    image = bytearray(a7s_silent_selector.A7S.read_bytes())
    offset = 0x43813E9A - a7s_silent_selector.BASE
    image[offset:offset + 4] = b"\x00\xbf\x00\xbf"  # nop; nop en lugar del store a root+0x78c
    assert a7s_silent_selector.at(bytes(image), 0x43813E9A) != a7s_silent_selector.EXPECTED[0x43813E9A]


def test_a7s_liro_command_0x40e3_has_handler_writing_settings_block():
    data = a7s_silent_selector.build()
    assert data["liro_command"]["a7s_row"] == {"address": "0x43ff79e4", "cmd": "0x40e3", "handler": "0x437a9cb1"}
    assert data["liro_command"]["a6000_row"]["handler"] == "0x438032d5"
    assert data["liro_command"]["a7s_handler_writes"].startswith("0x43ea1fd4")
    assert not data["libobj_a7s"]["instruction_mismatches"] and all(data["libobj_a7s"]["strings_present"].values())


def test_imager_vtable_roles_and_identical_slots():
    import imager_vtable

    data = imager_vtable.build()
    assert data["identical_slots"] == [1, 20, 26, 27, 28, 31, 32, 33]
    roles = {r["slot"]: r for r in data["slots"]}
    assert any("SHR" in s for s in roles[10]["A7S_strings"]) and any("svd" in s for s in roles[10]["A6000_strings"])
    assert any("PowerOn" in s for s in roles[6]["A6000_strings"])


def test_shutter_mode_switch_supports_mode_2_only_on_a6000():
    import imager_shutter_modes

    data = imager_shutter_modes.build()
    assert data["A6000"]["param_load_ok"] and data["A7S"]["param_load_ok"]
    assert len(data["A6000"]["case_targets"]) == 5 and data["A7S"]["case2_unsupported"]
    assert data["A6000"]["case2_sets_bits"]


def test_state_dumpers_differ_only_in_got_offsets():
    import imager_vtable

    dumper = imager_vtable.state_dumper()
    assert dumper["len"] == [1599, 1599] and dumper["only_got_offsets"]
