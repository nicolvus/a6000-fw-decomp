"""E25-02 — auditoría independiente de B1a y de la vía volátil InitCom.

No importa `scripts/e25/*` ni usa sus JSON: decodifica los bytes del candidato,
del tipo 0 y del original con controles diferenciales propios. Solo lectura.

Informe: docs/capture/e25-02-validacion-candidato-y-via-volatil.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts" / "e25_02")]

import audit as A

if not (A.ORIGINAL.exists() and A.TIPO0.exists() and A.CANDIDATE.exists()):
    pytest.skip("faltan los binarios de Darwin/tipo 0/candidato", allow_module_level=True)


@pytest.fixture(scope="module")
def original() -> A.Image:
    return A.Image(A.ORIGINAL)


@pytest.fixture(scope="module")
def tipo0() -> A.Image:
    return A.Image(A.TIPO0)


@pytest.fixture(scope="module")
def cand() -> A.Image:
    return A.Image(A.CANDIDATE)


@pytest.fixture(scope="module")
def report() -> dict:
    return A.build()


def at(img: A.Image, addr: int) -> str:
    return A.ins_at(img, addr)


# ------------------------------------------------------------------------------------------------ integridad


def test_candidate_sha_and_size(cand):
    assert cand.sha256() == A.SHA_CANDIDATE
    assert len(cand.data) == 157276


def test_inputs_are_the_expected_variants(original, tipo0):
    assert original.sha256() == A.SHA_ORIGINAL
    assert tipo0.sha256() == A.SHA_TIPO0


def test_candidate_diff_vs_tipo0_is_exactly_two_bytes(cand, tipo0):
    diff = [(original_addr, a, b) for original_addr, a, b in
            [(i + A.BASE, tipo0.data[i], cand.data[i]) for i in range(len(tipo0.data))]
            if a != b]
    assert diff == [(0x1FE6A, 0x28, 0x0A), (0x1FE6B, 0x46, 0xE0)]


def test_gate_branch_target_from_raw_encoding(cand):
    assert cand.bytes(0x1FE6A, 2) == bytes.fromhex("0ae0")
    assert A.branch_target_n(cand, 0x1FE6A) == 0x1FE82
    assert cand.u16(0x1FE6A) & 0xF800 == 0xE000  # B.N incondicional


def test_tipo0_patch_is_preserved(cand):
    assert cand.bytes(A.TIPO0_ADDR, 8) == A.TIPO0_BYTES
    assert at(cand, 0x20C78) == "b #0x20c8e"
    assert at(cand, 0x20C8E) == "pop {r4, pc}"


# ------------------------------------------------------------------------------------------------ función parcheada


def test_patched_function_shape(cand):
    assert at(cand, 0x1FE66) == "push {r4, r5, r6, lr}"
    assert at(cand, 0x1FE68) == "movs r5, #0"
    assert at(cand, 0x1FE6A) == "b #0x1fe82"
    assert at(cand, 0x1FE82) == "mov r0, r5"
    assert at(cand, 0x1FE84) == "pop {r4, r5, r6, pc}"


def test_patched_path_does_not_execute_the_gate_reader(cand):
    # El único BL a 0x1b080 sigue existiendo en el cuerpo, pero el salto lo deja fuera.
    assert at(cand, 0x1FE6C) == "bl #0x1b080"
    executed = [0x1FE66, 0x1FE68, 0x1FE6A, 0x1FE82, 0x1FE84]
    assert 0x1FE6C not in executed
    assert A.branch_target_n(cand, 0x1FE6A) == 0x1FE82


def test_patched_path_does_not_execute_the_tbb_table(cand):
    assert at(cand, 0x1FE76) == "tbb [pc, r4]"
    assert A.branch_target_n(cand, 0x1FE6A) == 0x1FE82
    # El salto va al epílogo, no a 0x1fe76 ni a 0x1fe80.
    assert A.branch_target_n(cand, 0x1FE6A) not in (0x1FE76, 0x1FE80)


def test_stack_and_registers_are_preserved(cand):
    assert at(cand, 0x1FE66) == "push {r4, r5, r6, lr}"
    assert at(cand, 0x1FE84) == "pop {r4, r5, r6, pc}"
    # El camino ejecutado es exactamente: push; r5=0; b; r0=r5; pop.
    executed = [f"{i.address:#x}: {i.mnemonic} {i.op_str}"
                for i in list(cand.dis(0x1FE66, 6)) + list(cand.dis(0x1FE82, 4))]
    assert executed == [
        "0x1fe66: push {r4, r5, r6, lr}",
        "0x1fe68: movs r5, #0",
        "0x1fe6a: b #0x1fe82",
        "0x1fe82: mov r0, r5",
        "0x1fe84: pop {r4, r5, r6, pc}",
    ]


def test_return_value_is_zero_for_any_gate_byte(report):
    assert report["gate_semantics"]["candidate_summary"] == "0 siempre"
    for nibble in range(16):
        assert report["gate_semantics"]["candidate_values_0_to_15"][hex(nibble)] == 0


def test_original_gate_semantics_for_control(original):
    assert A.original_gate_value(0x00) == 0
    assert A.original_gate_value(0x10) == 1
    assert A.original_gate_value(0x20) == 2
    assert A.original_gate_value(0x30) == 3
    assert A.original_gate_value(0x40) == 4
    assert A.original_gate_value(0x50) == 5
    assert A.original_gate_value(0x60) == 0
    assert A.original_gate_value(0xF0) == 0


# ------------------------------------------------------------------------------------------------ tres arrancadores


def test_three_starters_call_the_same_thunk(cand):
    for addr in (0x1FEEE, 0x1FF80, 0x1FFDC):
        got = list(cand.dis(addr, 4))
        assert got and got[0].mnemonic == "bl"
        assert got[0].operands[0].imm == 0x1F5A2


def test_starters_choose_L0_with_gate_zero(report):
    for name, s in report["starters"].items():
        assert s["gate0_list"] == "0x29cd8", name
        assert s["gate0_ids"] == [0, 7, 8, 9, 10], name
    assert report["starters"]["load 0x1fee2"]["gate4_ids"] == [0, 2, 3, 6, 9, 10]
    assert report["starters"]["capture4 0x1ff72"]["gate4_ids"] == [0, 4, 5, 6, 9, 10]
    assert report["starters"]["capture5/1f 0x1ffce"]["gate4_ids"] == [0, 1, 4, 5, 6, 9, 10]


def test_lists_are_the_verified_four(cand):
    assert A.list_bytes(cand, 0x29CD8) == [0, 7, 8, 9, 10]
    assert A.list_bytes(cand, 0x29CDD) == [0, 2, 3, 6, 9, 10]
    assert A.list_bytes(cand, 0x29CE3) == [0, 4, 5, 6, 9, 10]
    assert A.list_bytes(cand, 0x29CE9) == [0, 1, 4, 5, 6, 9, 10]


def test_outer_table_has_states_2_and_4_outside_L0(cand, report):
    table = A.outer_table(cand)
    assert table[2] == 0x20120
    assert table[4] == 0x20134
    assert 2 not in A.list_bytes(cand, 0x29CD8)
    assert 4 not in A.list_bytes(cand, 0x29CD8)
    assert report["outer"]["state2_starts_inner"] == "0x20126"
    assert report["outer"]["state4_starts_inner"] == "0x2013a"


def test_inner_machine_entries_are_not_indirectly_reachable(cand, report):
    assert cand.bl_callers(0x1F396) == [0x20126]
    assert cand.bl_callers(0x1F3B6) == [0x2013A]
    assert report["outer"]["inner_entry_word_refs"]["0x1f396"] == []
    assert report["outer"]["inner_entry_word_refs"]["0x1f3b6"] == []
    assert cand.imm_refs({0x1F396, 0x1F3B6}) == []


# ------------------------------------------------------------------------------------------------ tipo 0 / P4D-P4E


def test_type_zero_filters_p4d_and_p4e(cand, report):
    assert at(cand, 0x20C74) == "push {r4, lr}"
    assert at(cand, 0x20C78) == "b #0x20c8e"
    assert at(cand, 0x20C8E) == "pop {r4, pc}"
    assert at(cand, 0x20C90) == "push {r4, lr}"
    assert at(cand, 0x20C92) == "bl #0x20c74"
    assert at(cand, 0x20C9E) == "cmp r0, #3"
    assert at(cand, 0x20CA2) == "pop.w {r4, lr}"  # sale antes de 0x51c0
    assert at(cand, 0x20CAC) == "b.w #0x51c0"
    assert report["tipo0"]["unchanged_vs_tipo0"] is True


def test_p4d_p4e_writers_are_all_behind_type_zero(cand):
    for addr in (0x20C90, 0x20CB2, 0x20CD4, 0x20D00):
        got = list(cand.dis(addr, 0x10))
        assert got[0].mnemonic == "push"
        assert any(i.mnemonic == "bl" and i.operands[0].imm == 0x20C74 for i in got), hex(addr)


# ------------------------------------------------------------------------------------------------ consumidores


def test_consumer_set_is_exactly_the_twelve_known_sites(cand, report):
    sites = {f"{a:#x}" for a in cand.bl_callers(0x1FE66)}
    assert sites == {
        "0x1f4ba", "0x1f4de", "0x1f576", "0x1f5a2", "0x1f5a8", "0x1f896",
        "0x1f908", "0x1fa40", "0x1fe88", "0x1fe90", "0x1fe98", "0x201bc",
    }
    assert set(report["consumers"]) == sites


def test_service_pulse_requires_gate_four(cand):
    # 0x1f4b6: if (0x1fe66() != 4) return; else call 0x1f474.
    assert at(cand, 0x1F4BA) == "bl #0x1fe66"
    assert at(cand, 0x1F4BE) == "cmp r0, #4"
    assert at(cand, 0x1F4C0) == "bne #0x1f4cc"
    assert at(cand, 0x1F4CA) == "b #0x1f474"


def test_lever_check_skips_error_six_with_gate_zero(cand):
    assert at(cand, 0x1F4DE) == "bl #0x1fe66"
    assert at(cand, 0x1F4E2) == "cmp r0, #0"
    assert at(cand, 0x1F4E4) == "beq #0x1f51c"
    assert at(cand, 0x1F516) == "movs r0, #6"
    assert at(cand, 0x1F518) == "b.w #0x16558"


def test_lever_read_returns_zero_with_gate_zero(cand):
    assert at(cand, 0x1F576) == "bl #0x1fe66"
    assert at(cand, 0x1F57A) == "cbz r0, #0x1f59e"
    assert at(cand, 0x1F59E) == "mov r0, r4"
    assert at(cand, 0x1F5A0) == "pop {r4, pc}"


def test_direct_rearm_returns_immediately_with_gate_zero(cand):
    assert at(cand, 0x1F5A8) == "bl #0x1fe66"
    assert at(cand, 0x1F5AC) == "cmp r0, #0"
    assert at(cand, 0x1F5AE) == "beq #0x1f5fe"
    assert at(cand, 0x1F5B8) == "bl #0x1fe50"


def test_inner_state_896_skips_coil_with_gate_zero(cand):
    assert at(cand, 0x1F896) == "bl #0x1fe66"
    assert at(cand, 0x1F89A) == "cmp r0, #1"
    assert at(cand, 0x1F89E) == "cmp r0, #2"
    assert at(cand, 0x1F8A0) == "bne #0x1f8a6"
    assert at(cand, 0x1F8A2) == "bl #0x20c90"


def test_inner_state_908_calls_coil_but_type_zero_filters(cand):
    assert at(cand, 0x1F908) == "bl #0x1fe66"
    assert at(cand, 0x1F90C) == "cmp r0, #1"
    assert at(cand, 0x1F910) == "cmp r0, #2"
    assert at(cand, 0x1F914) == "bl #0x20c90"


def test_timeout_emits_error_six_only_inside_inner_machine(cand):
    assert at(cand, 0x1FA40) == "bl #0x1fe66"
    assert at(cand, 0x1FA44) == "cmp r0, #4"
    assert at(cand, 0x1FA46) == "bne #0x1faa8"
    assert at(cand, 0x1FAB8) == "bl #0x16558"


def test_motor_two_requires_gate_one_two_or_four(cand):
    assert at(cand, 0x1FE88) == "bl #0x1fe66"
    assert at(cand, 0x1FE8C) == "cmp r0, #4"
    assert at(cand, 0x1FE94) == "cmp r0, #1"
    assert at(cand, 0x1FE9C) == "cmp r0, #2"
    assert at(cand, 0x1FEA0) == "bl #0x1fe32"
    assert at(cand, 0x1FEB0) == "b.w #0x51cc"


def test_state_guard_201b0_clears_with_gate_zero(cand):
    assert at(cand, 0x201B4) == "bl #0x20c74"
    assert at(cand, 0x201BC) == "bl #0x1fe66"
    assert at(cand, 0x201C0) == "cbz r0, #0x201c8"
    assert at(cand, 0x201C8) == "movs r0, #0"


def test_no_gate_consumer_in_reset_initcom_upd_off(cand):
    for start, end in ((0x45C8, 0x4638), (0x4BCA, 0x5000), (0x8DA8, 0x8E00), (0x8900, 0x8C90)):
        assert not any(start <= a < end for a in cand.bl_callers(0x1FE66))


# ------------------------------------------------------------------------------------------------ motor, op5, pines, cancelación


def test_motor_callers_are_the_known_set_and_are_classified(report):
    assert report["motor_callers"]["0x1fe50"] == [
        {"site": "0x1f47c", "class": "pulse 0x1f474 (solo desde 0x1f4b6, que exige gate==4)"},
        {"site": "0x1f5b8", "class": "rearme directo 0x1f5a6 (retorna si gate==0)"},
        {"site": "0x1f6e0", "class": "máquina interior 27 estados"},
        {"site": "0x1f730", "class": "máquina interior 27 estados"},
    ]
    assert report["motor_callers"]["0x1feb6"][-1] == {
        "site": "0x1fcba", "class": "operación 5 (sin compuerta)"}


def test_no_absolute_pointer_to_gate_or_motor(cand, report):
    for addr in (0x1FE66, 0x1FE50, 0x1FE86, 0x1FEB6, 0x1F5A6, 0x1FCB8):
        assert cand.word_refs(addr) == [], hex(addr)
        assert cand.imm_refs({addr}) == [], hex(addr)
    for v in report["motor_absolute_refs"].values():
        assert v["word_refs"] == [] and v["imm_refs"] == []


def test_operation_five_is_an_off_pattern_not_a_movement_order(cand, report):
    assert at(cand, 0x1F606) == "bl #0x1fcb8"
    assert at(cand, 0x1FCBA) == "bl #0x1feb6"
    assert at(cand, 0x1FEBC) == "movs r1, #3"
    assert at(cand, 0x1FEC2) == "movw r2, #0xfffc"
    assert at(cand, 0x1FEC6) == "movs r0, #4"
    assert at(cand, 0x1FEC8) == "b.w #0x51cc"
    assert report["operation5"]["p40"] == 1
    assert report["operation5"]["p41"] == 1
    assert report["operation5"]["xor"] == 0
    assert "no es una orden de movimiento" in report["operation5"]["meaning"]


def test_p4b_and_p4c_stay_active(cand, report):
    assert cand.bl_callers(0x1ECEC) == [0x16E6C, 0x16E7E, 0x17096]
    assert at(cand, 0x1ECEC) == "mov.w r2, #0x230"
    assert at(cand, 0xD176) == "mov.w r0, #0x22c"
    assert at(cand, 0xD1E8) == "mov.w r0, #0x22c"
    assert report["pins"]["P4C"]["patch_untouched"] is True
    assert report["pins"]["P4B"]["patch_untouched"] is True


def test_initcom_stop_is_not_a_capture_cancel(cand, report):
    assert cand.bl_callers(0x4ED8) == [0xED1A]
    assert cand.bl_callers(0xED18) == [0x750C]
    assert 0x750C in range(0x747A, 0x755C)
    assert report["cancellation"]["actual"].startswith("bandera de parada")


def test_real_abort_candidate_goes_to_operation_five(cand, report):
    assert at(cand, 0x16DE6) == "movs r1, #0x30"
    assert at(cand, 0x16DE8) == "movs r0, #2"
    assert at(cand, 0x16DEA) == "bl #0x16558"
    assert "op5" in report["cancellation"]["real_abort_candidate"]
    assert "sin compuerta" in report["cancellation"]["real_abort_effect"]


# ------------------------------------------------------------------------------------------------ InitCom / vía volátil


def test_initcom_dispatches_only_four_commands(cand, report):
    assert report["initcom"]["dispatch"] == ["cmp r1, #0x11", "cmp r1, #0x12",
                                             "cmp r1, #0x13", "cmp r1, #0x16"]


def test_initcom_0x16_write_is_not_selective(cand, report):
    assert at(cand, 0x4CFC) == "ldrb.w r4, [sp, #0x19]"
    assert at(cand, 0x4D02) == "and r0, r4, #0x7f"
    assert at(cand, 0x4D0A) == "lsls r0, r4, #0x18"
    assert at(cand, 0x4DC8) == "mov r2, r4"
    assert at(cand, 0x4DCE) == "bl #0x255a6"
    w = report["initcom"]["command_0x16_write"]
    assert w["copy_length_with_bit7"] == 129
    assert w["copy_length_masked"] == 1
    assert w["bytes_written"] == 129
    assert w["selective_one_byte"] is False
    assert report["initcom_write_demo"]["written_bytes"] == 129
    assert report["initcom_write_demo"]["end_exclusive"] == "0x200000d1"


def test_initcom_0x16_read_is_selective_but_has_no_sender(cand, report):
    assert at(cand, 0x4DD8) == "movs r1, #0x78"
    assert at(cand, 0x4DDC) == "bl #0x25642"
    assert at(cand, 0x4DE0) == "mov r2, r4"
    assert at(cand, 0x4DE6) == "bl #0x255a6"
    assert report["initcom"]["command_0x16_read"]["copy_length"] == 1
    assert report["initcom"]["command_0x16_read"]["selective"] is True


def test_initcom_0x12_writes_a_full_block(cand, report):
    assert at(cand, 0x4D40) == "add r0, sp, #0x14"
    assert at(cand, 0x4D4A) == "ldrb.w r2, [sp, #0x19]"
    assert at(cand, 0x4D68) == "bl #0x255a6"
    b = report["initcom"]["command_0x12_block"]
    assert b["block_bytes"] == 0x78
    assert b["gate_offset"] == "0x50"
    assert "0x40" in b["watchdog_offsets"]
    assert b["selective"] is False


def test_initcom_lives_only_in_seton(cand, report):
    assert cand.bl_callers(0x4BCA) == [0xECFE]
    assert report["initcom"]["window"]["com_task"] == "0xece4"
    ldr = next(iter(cand.dis(0x7460, 4)))
    assert ldr.mnemonic == "ldr"
    op = ldr.operands[1]
    lit = ((ldr.address + 4) & ~3) + op.mem.disp
    assert cand.u32(lit) == 0xECE5
    assert at(cand, 0x7462) == "bl #0x4504"


def test_no_static_writer_of_the_gate(cand):
    assert cand.word_refs(0x20000050) == []
    assert cand.word_refs(0x22000A00) == []
    # El único acceso estático a +0x50 es la lectura de 0x1b080.
    assert at(cand, 0x1B090) == "ldrb.w r0, [r0, #0x50]"


# ------------------------------------------------------------------------------------------------ veredictos


def test_final_verdicts(report):
    v = report["verdicts"]
    assert v["A_volatile"] == "NO"
    assert v["B1a_static"] == "VÁLIDO ESTÁTICAMENTE"
    assert v["M0_normal_static"] == "SÍ"
    assert v["M0_physical"] == "NO MEDIDO"
    assert v["M1_capture_complete"] == "NO DEMOSTRADO"
    assert v["recovery"] == "NO DEMOSTRADA"
    assert v["installable"] == "NO"
