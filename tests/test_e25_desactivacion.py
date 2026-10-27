"""E25 — desactivación del rearme mecánico: bytes, selección de listas, parcheo y reversión.

Lee `darwin_core.bin` 3.21 y la copia tipo 0 (no versionados); se omite si faltan. No ejecuta
firmware, no toca la cámara y no genera FDAT/DAT. Informe: docs/capture/e25-desactivacion-mecanica.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

capstone = pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts" / "e25"), str(ROOT / "scripts" / "e24_05")]

from analyze import mechanical, route_a
from capstone import arm
from dwn import BASE, DARWIN, SHA256, Core
from patch_darwin import (
    ORIGINAL,
    PATCH_ADDR,
    PATCH_NEW,
    PATCH_OLD,
    SHA_TIPO0,
    TIPO0,
    TIPO0_ADDR,
    TIPO0_BYTES,
    DarwinImage,
    ImageError,
    apply,
    inspect,
    restore,
    verify,
)

if not DARWIN.exists():
    pytest.skip(f"falta {DARWIN.relative_to(ROOT)}", allow_module_level=True)

TIPO0_PATH = ROOT / "analysis/darwin-patch/darwin_core_tipo0.bin"


@pytest.fixture(scope="module")
def c() -> Core:
    core = Core()
    assert core.sha256() == SHA256
    return core


@pytest.fixture(scope="module")
def mech(c):
    return mechanical(c)


@pytest.fixture(scope="module")
def route(c):
    return route_a(c)


@pytest.fixture(scope="module")
def tipo0() -> Path:
    if not TIPO0_PATH.exists():
        pytest.skip("falta analysis/darwin-patch/darwin_core_tipo0.bin")
    assert DarwinImage.load(TIPO0_PATH).variant == TIPO0
    return TIPO0_PATH


@pytest.fixture(scope="module")
def patched(tmp_path_factory, tipo0):
    out = tmp_path_factory.mktemp("e25") / "tipo0_sin_rearme.bin"
    manifest = tmp_path_factory.mktemp("e25") / "manifest.json"
    m = apply(tipo0, out, manifest)
    return out, manifest, m


def ins(core: Core, addr: int, n: int) -> dict[int, str]:
    return {i.address: f"{i.mnemonic} {i.op_str}" for i in core.dis(addr, n)}


def row(mech, name: str, gate: int, coil: int = 0) -> dict:
    return next(r for r in mech["reachability"] if r["name"] == name and r["gate"] == gate and r["coil"] == coil)


# ---------------------------------------------------------------------------------------------- variantes


def test_original_variant_identified():
    img = DarwinImage.load(DARWIN)
    assert img.variant == ORIGINAL and not img.patched
    assert img.variant.tipo0_present is False
    assert img.variant.m0_candidate is False
    assert img.bytes(TIPO0_ADDR, len(TIPO0_BYTES)) == bytes.fromhex("faf702fa00f00700")


def test_tipo0_variant_identified(tipo0):
    img = DarwinImage.load(tipo0)
    assert img.variant == TIPO0 and not img.patched
    assert img.variant.tipo0_present is True
    assert img.variant.m0_candidate is True
    assert img.bytes(TIPO0_ADDR, len(TIPO0_BYTES)) == TIPO0_BYTES


def test_unknown_sha_rejected(tmp_path):
    data = bytearray(DARWIN.read_bytes())
    data[0x1000] ^= 0xFF
    bad = tmp_path / "bad.bin"
    bad.write_bytes(data)
    with pytest.raises(ImageError, match="SHA-256 desconocido"):
        DarwinImage.load(bad)


def test_wrong_size_rejected(tmp_path):
    bad = tmp_path / "bad.bin"
    bad.write_bytes(DARWIN.read_bytes()[:100])
    with pytest.raises(ImageError, match="tamaño inesperado"):
        DarwinImage.load(bad)


def test_wrong_version_rejected(tmp_path):
    data = bytearray(DARWIN.read_bytes())
    data[0x25B3C - BASE:0x25B3C - BASE + 8] = b"VER0.79\x00"
    bad = tmp_path / "bad.bin"
    bad.write_bytes(data)
    with pytest.raises(ImageError, match="versión inesperada"):
        DarwinImage.load(bad)


def test_tipo0_bytes_are_exact_and_differ_from_original(c, tipo0):
    assert c.data[TIPO0_ADDR - BASE:TIPO0_ADDR - BASE + len(TIPO0_BYTES)] == bytes.fromhex("faf702fa00f00700")
    t = DarwinImage.load(tipo0)
    assert t.bytes(TIPO0_ADDR, len(TIPO0_BYTES)) == TIPO0_BYTES
    assert inspect(tipo0)["variant"] == "tipo0_322"
    assert inspect(DARWIN)["variant"] == "original_321"


# ---------------------------------------------------------------------------------------------- parcheo


def test_apply_changes_only_the_authorized_two_bytes(patched):
    out, _, m = patched
    assert len(m["diff"]) == 2
    assert [d["rom_address"] for d in m["diff"]] == [PATCH_ADDR, PATCH_ADDR + 1]
    assert [(d["before"], d["after"]) for d in m["diff"]] == [("28", "0a"), ("46", "e0")]
    img = DarwinImage.load(out)
    assert img.patched and img.variant == TIPO0
    assert img.bytes(PATCH_ADDR, 2) == PATCH_NEW
    assert img.bytes(PATCH_ADDR, 2) != PATCH_OLD


def test_apply_is_deterministic(tmp_path, tipo0, patched):
    out, _, m1 = patched
    out2 = tmp_path / "again.bin"
    m2 = apply(tipo0, out2)
    assert m1["output"]["sha256"] == m2["output"]["sha256"]
    assert m1["diff"] == m2["diff"]
    assert out.read_bytes() == out2.read_bytes()


def test_apply_refuses_to_overwrite_input(tipo0):
    with pytest.raises(ImageError, match="mismo archivo"):
        apply(tipo0, tipo0)


def test_apply_refuses_installable_package(tmp_path, tipo0):
    with pytest.raises(ImageError, match=".fdat/.dat"):
        apply(tipo0, tmp_path / "candidate.fdat")
    with pytest.raises(ImageError, match=".fdat/.dat"):
        apply(tipo0, tmp_path / "candidate.dat")


def test_apply_refuses_double_patch(patched, tmp_path):
    out, _, _ = patched
    with pytest.raises(ImageError, match="ya lleva"):
        apply(out, tmp_path / "twice.bin")


def test_restore_is_exact(patched, tmp_path, tipo0):
    out, manifest, _ = patched
    restored = tmp_path / "restored.bin"
    r = restore(out, restored, manifest)
    assert r["matches_manifest_input"] is True
    assert restored.read_bytes() == tipo0.read_bytes()
    assert r["sha256"] == SHA_TIPO0


def test_verify_accepts_only_the_authorized_patch(patched, tipo0, tmp_path):
    out, manifest, _ = patched
    assert verify(tipo0, out, manifest)["output"]["sha256"] == DarwinImage.load(out).sha256()
    bad = tmp_path / "bad.bin"
    data = bytearray(out.read_bytes())
    data[0x20000 - BASE] ^= 1
    bad.write_bytes(data)
    with pytest.raises(ImageError, match="cambios distintos"):
        verify(tipo0, bad, manifest)


def test_manifest_protected_regions_are_unchanged(patched):
    _, _, m = patched
    p = m["preserved"]
    assert m["schema"] == "a6000.e25.manifest.v1"
    assert m["patch"]["id"] == "E25-GATE-ZERO"
    assert m["safety"]["installable"] is False
    assert m["safety"]["fdat_generated"] is False
    assert p["all_protected_unchanged"] is True
    assert all(x["unchanged"] for x in p["protected_regions"])
    names = {x["name"] for x in p["protected_regions"]}
    assert {"reset", "initcom", "watchdog", "power_table", "upd_main", "bootloader_mailbox"} <= names
    for x in p["protected_regions"]:
        assert not (int(x["start"], 16) <= PATCH_ADDR < int(x["end"], 16))


def test_manifest_marks_original_as_not_m0(tipo0, tmp_path):
    m = apply(DARWIN, tmp_path / "original_gate.bin")
    assert m["input"]["variant"] == "original_321"
    assert m["input"]["tipo0_present"] is False
    assert m["safety"]["m0_candidate"] is False
    assert m["safety"]["requires_tipo0"] is True


def test_manifest_marks_tipo0_as_m0(patched):
    _, _, m = patched
    assert m["input"]["variant"] == "tipo0_322"
    assert m["input"]["tipo0_present"] is True
    assert m["safety"]["m0_candidate"] is True
    assert m["preserved"]["tipo0"]["unchanged"] is True


def test_no_installable_artifacts_written(patched, tmp_path):
    out, _, m = patched
    assert out.suffix == ".bin"
    assert not list(out.parent.glob("*.fdat"))
    assert not list(out.parent.glob("*.dat"))
    assert m["safety"]["fdat_generated"] is False


# ---------------------------------------------------------------------------------------------- bytes de la compuerta


def test_gate_patch_semantics(patched):
    out, _, _ = patched
    pc = Core(out)
    a = ins(pc, 0x1FE66, 0x20)
    assert a[0x1FE68] == "movs r5, #0"
    assert a[0x1FE6A] == "b #0x1fe82"
    assert a[0x1FE82] == "mov r0, r5"
    assert a[0x1FE84] == "pop {r4, r5, r6, pc}"
    assert a[0x1FE66] == "push {r4, r5, r6, lr}"
    # El salto incondicional deja 0x1fe6c/0x1fe76 fuera del camino; r5=0 y el epílogo lo devuelve.
    assert a[0x1FE6C] == "bl #0x1b080"
    assert a[0x1FE6A] == "b #0x1fe82"


def test_original_gate_reads_high_nibble_and_table(c):
    a = ins(c, 0x1FE66, 0x20)
    assert a[0x1FE6C] == "bl #0x1b080"
    assert a[0x1FE70] == "lsrs r4, r0, #4"
    assert a[0x1FE72] == "cmp r4, #6"
    assert c.data[0x1FE7A - BASE:0x1FE7A - BASE + 6] == bytes([4, 3, 3, 3, 3, 3])
    assert ins(c, 0x1B080, 0x18)[0x1B090] == "ldrb.w r0, [r0, #0x50]"


def test_gate_patch_branch_encoding(patched):
    out, _, _ = patched
    assert out.read_bytes()[PATCH_ADDR - BASE:PATCH_ADDR - BASE + 2] == bytes.fromhex("0ae0")
    assert ins(Core(out), PATCH_ADDR, 2)[PATCH_ADDR] == "b #0x1fe82"


def test_tipo0_patch_preserved_and_still_zero(patched):
    out, _, _ = patched
    pc = Core(out)
    assert pc.data[0x20C74 - BASE:0x20C90 - BASE] == DarwinImage.load(TIPO0_PATH).data[0x20C74 - BASE:0x20C90 - BASE]
    a = ins(pc, 0x20C74, 0x20)
    assert a[0x20C78] == "b #0x20c8e"
    assert a[0x20C8E] == "pop {r4, pc}"


def test_state7_p4d_writer_is_gated_by_type0(mech, c):
    assert "0x20c90" in mech["outer"]["state7_calls"]
    a = ins(c, 0x20C90, 0x20)
    assert a[0x20C92] == "bl #0x20c74" and a[0x20C96] == "cmp r0, #0"
    assert a[0x20C98] == "beq #0x20cb0"
    assert a[0x20CA2] == "pop.w {r4, lr}"  # el camino tipo 0 sale antes de 0x51c0
    assert a[0x20CAC] == "b.w #0x51c0"


# ---------------------------------------------------------------------------------------------- listas y máquina exterior


def test_lists_are_the_verified_four(c):
    assert bytes(c.data[0x29CD8 - BASE:0x29CF0 - BASE]) == bytes([0, 7, 8, 9, 10, 0, 2, 3, 6, 9, 10,
                                                                 0, 4, 5, 6, 9, 10, 0, 1, 4, 5, 6, 9, 10])
    assert list(c.data[0x29CD8 - BASE:0x29CD8 - BASE + 5]) == [0, 7, 8, 9, 10]


def test_three_starters_select_L0_with_gate_zero(mech):
    for name, s in mech["starters"].items():
        assert s["gate0_list"] == "0x29cd8", name
        assert s["gate0_ids"] == [0, 7, 8, 9, 10], name
    assert mech["starters"]["load 0x1fee2"]["gate4_ids"] == [0, 2, 3, 6, 9, 10]
    assert mech["starters"]["capture 4 0x1ff72"]["gate4_ids"] == [0, 4, 5, 6, 9, 10]
    assert mech["starters"]["capture 5/1f 0x1ffce"]["gate4_ids"] == [0, 1, 4, 5, 6, 9, 10]


def test_outer_handlers_and_terminal(mech):
    assert mech["lists"]["L0"]["ids"] == [0, 7, 8, 9, 10]
    assert mech["outer"]["terminal"] == 0x0A
    assert mech["outer"]["handlers"] == {
        "0": "0x20100", "1": "0x2011c", "2": "0x20120", "3": "0x200e2", "4": "0x20134",
        "5": "0x200e2", "6": "0x20148", "7": "0x2014c", "8": "0x200e2", "9": "0x200e6", "10": "0x200fc",
    }
    assert [h["handler"] for h in mech["outer"]["L0_handlers"]] == [
        "0x20100", "0x2014c", "0x200e2", "0x200e6", "0x200fc"]


def test_L0_completes_with_occupancy_release(mech, c):
    assert "0xd18e" in mech["outer"]["state9_calls"]
    assert ins(c, 0x200E6, 0x18)[0x200EA] == "mov.w r0, #0x1000000"
    assert ins(c, 0x200E6, 0x18)[0x200EE] == "bl #0xd18e"
    # estado 0 marca ocupado; estado 10 termina
    assert ins(c, 0x20100, 0x18)[0x20104] == "movs r0, #1"
    assert ins(c, 0x20100, 0x18)[0x20106] == "bl #0x2016e"
    assert ins(c, 0x200FC, 4)[0x200FC] == "b.w #0x1e4f6"


def test_L0_does_not_start_inner_machine(c, mech):
    assert c.bl_callers(0x1F396) == [0x20126]
    assert c.bl_callers(0x1F3B6) == [0x2013A]
    assert mech["lists"]["L0"]["ids"] == [0, 7, 8, 9, 10]
    assert 2 not in mech["lists"]["L0"]["ids"] and 4 not in mech["lists"]["L0"]["ids"]


def test_m49_states_4_5_1f_choose_L0(mech):
    for name in ("m49_4", "m49_5", "m49_1f"):
        assert row(mech, name, 0)["states"] == [0, 7, 8, 9, 10]
        assert row(mech, name, 0)["motor_primitives"] == []
        assert row(mech, name, 4)["motor_primitives"], name


def test_capture_apis_zero_motor_with_gate_zero(mech):
    for name in ("capture4", "capture5", "capture1f"):
        assert row(mech, name, 0)["states"] == [0, 7, 8, 9, 10]
        assert row(mech, name, 0)["motor_primitives"] == []
        assert row(mech, name, 4)["motor_primitives"]


def test_single_shot_and_burst_paths_zero_motor(mech):
    for name in ("burst_prep", "rearm_burst", "capture_task"):
        assert row(mech, name, 0)["states"] == [0, 7, 8, 9, 10], name
        assert row(mech, name, 0)["motor_primitives"] == [], name
        assert row(mech, name, 4)["motor_primitives"], name


def test_load_zero_motor_and_L0(mech):
    r = row(mech, "load", 0)
    assert r["states"] == [0, 7, 8, 9, 10] and r["motor_primitives"] == []
    r1 = row(mech, "load(1)", 0)
    assert r1["states"] == [0, 7, 8, 9, 10] and r1["motor_primitives"] == []


# ---------------------------------------------------------------------------------------------- motor, freno y excepciones


def test_operation5_keeps_only_the_ungated_brake(mech):
    assert mech["operation5"]["0"]["motor_primitives"] == ["0x1feb6"]
    assert mech["operation5"]["0"]["brake"] == ["0x1fcb8"]
    assert mech["operation5"]["4"]["motor_primitives"] == ["0x1fe50", "0x1feb6"]


def test_brake_is_value_3_and_xor_is_zero(c):
    a = ins(c, 0x1FEB6, 0x18)
    assert a[0x1FEB8] == "bl #0x1fe32"
    assert a[0x1FEBC] == "movs r1, #3"
    assert a[0x1FEC2] == "movw r2, #0xfffc"
    assert a[0x1FEC6] == "movs r0, #4"
    assert a[0x1FEC8] == "b.w #0x51cc"
    assert (3 & 1) ^ ((3 >> 1) & 1) == 0
    assert (1 & 1) ^ ((1 >> 1) & 1) == 1 and (2 & 1) ^ ((2 >> 1) & 1) == 1


def test_brake_path_is_untouched_by_the_patch(patched):
    out, _, m = patched
    assert all(d["rom_address"] not in (0x1F600, 0x1FCB8, 0x1FEB6) for d in m["diff"])
    assert out.read_bytes()[0x1FCB8 - BASE:0x1FCD8 - BASE] == DARWIN.read_bytes()[0x1FCB8 - BASE:0x1FCD8 - BASE]


def test_lever_error_is_skipped_with_gate_zero(mech):
    assert mech["errors"]["lever_0x1f4ce"]["0"]["error6"] == []
    assert mech["errors"]["lever_0x1f4ce"]["4"]["error6"] == ["0x1f518"]


def test_timeout_error6_is_only_inside_the_inner_machine(mech):
    assert "0x1fab8" in mech["errors"]["timeout_0x1fa3a"]["0"]["error6"]
    # La máquina interior solo se arranca en los estados 2/4; L0 no los contiene.
    ids = mech["lists"]["L0"]["ids"]
    assert 2 not in ids and 4 not in ids


def test_load_can_still_raise_adc_error6(mech):
    assert "0x1989c" in row(mech, "load", 0)["error6"]
    assert "0x1989c" in row(mech, "load(1)", 0)["error6"]


def test_motor_primitive_callers_are_closed_and_known(c):
    owners = {p: sorted(c.bl_callers(p)) for p in (0x1FE50, 0x1FE86, 0x1FEB6)}
    assert owners[0x1FE50] == [0x1F47C, 0x1F5B8, 0x1F6E0, 0x1F730]
    assert owners[0x1FE86] == [0x1F482, 0x1F65C, 0x1FC10]
    assert owners[0x1FEB6] == [0x1F49C, 0x1F686, 0x1F7BE, 0x1FBDC, 0x1FC34, 0x1FCBA]
    assert c.bl_callers(0x1F5A6) == [0x2063A]
    assert c.bl_callers(0x1FCB8) == [0x1F5FA, 0x1F606]


def test_p4d_p4e_writers_are_not_reached_with_type0(c):
    # Los cuatro escritores de bobina consultan 0x20c74 antes de 0x51c0.
    for f in (0x20C90, 0x20CB2, 0x20CD4, 0x20D00):
        calls = [i.operands[0].imm for i in c.dis(f, 0x40)
                 if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].type == arm.ARM_OP_IMM]
        assert 0x20C74 in calls, hex(f)
    # El camino tipo 0 de 0x20c90 retorna antes del único `b.w 0x51c0`.
    a = ins(c, 0x20C90, 0x24)
    assert a[0x20C98] == "beq #0x20cb0" and a[0x20CA2] == "pop.w {r4, lr}"
    assert a[0x20CAC] == "b.w #0x51c0"


def test_gate_zero_does_not_filter_every_p4d_caller(c):
    # 0x1f908 cae a 0x20c90 cuando la compuerta vale 0 (0 no es 1 ni 2): el filtro que evita
    # la escritura es 0x20c74 (tipo 0), no la compuerta. 0x1f896 sí se salta la llamada.
    a = ins(c, 0x1F8FC, 0x30)
    assert a[0x1F908] == "bl #0x1fe66"
    assert a[0x1F90E] == "beq #0x1f918" and a[0x1F912] == "beq #0x1f918"
    assert a[0x1F914] == "bl #0x20c90"
    b = ins(c, 0x1F88A, 0x24)
    assert b[0x1F896] == "bl #0x1fe66"
    assert b[0x1F89C] == "beq #0x1f8a2" and b[0x1F8A0] == "bne #0x1f8a6"


def test_p4c_set_to_one_exists_and_is_separate(c):
    a = ins(c, 0x1ECEC, 0x10)
    assert a[0x1ECEC] == "mov.w r2, #0x230"
    assert a[0x1ECF0] == "cbz r0, #0x1ecf6"
    assert a[0x1ECF2] == "movs r1, #1"
    assert a[0x1ECF8] == "mov r0, r2"
    assert a[0x1ECFA] == "b.w #0x51c0"
    assert c.bl_callers(0x1ECEC) == [0x16E6C, 0x16E7E, 0x17096]
    assert ins(c, 0x16E7A, 4)[0x16E7C] == "movs r0, #1"
    assert ins(c, 0x16E68, 4)[0x16E6A] == "movs r0, #0"


def test_p4b_uses_occupancy_masks_not_the_motor(c):
    # P4B = bit 11 (0x800) en las máscaras de 0xd116/0xd18e; no pasa por 0x1fe66.
    for f in (0xD116, 0xD18E):
        assert not any(i.mnemonic == "bl" and i.operands and i.operands[0].imm == 0x1FE66 for i in c.dis(f, 0x30))
    assert c.bl_callers(0x1FE66) == [0x1F4BA, 0x1F4DE, 0x1F576, 0x1F5A2, 0x1F5A8, 0x1F896,
                                    0x1F908, 0x1FA40, 0x1FE88, 0x1FE90, 0x1FE98, 0x201BC]


# ---------------------------------------------------------------------------------------------- vía volátil


def test_no_static_writer_of_the_gate(route):
    w = route["gate"]["static_writers"]
    assert w["literal_0x20000050_users"] == []
    assert w["literal_0x22000a00_users"] == []
    assert w["direct_base_plus_0x50_candidates"] == []


def test_initcom_0x12_writes_a_whole_block(c):
    a = ins(c, 0x4D40, 0x30)
    assert a[0x4D50] == "movs r1, #0x78"
    assert a[0x4D52] == "udiv r4, r0, r1"
    assert a[0x4D56] == "mls r1, r1, r4, r0"
    assert a[0x4D5A] == "cbz r1, #0x4d62"
    assert a[0x4D62] == "mov r1, r7"
    assert a[0x4D64] == "add.w r0, r0, #0x20000000"
    assert a[0x4D68] == "bl #0x255a6"


def test_initcom_0x12_model_touches_the_whole_block(route):
    m = route["initcom"]["command_0x12"]
    assert m["selective"] is False
    assert m["block_bytes_written_to_reach_gate"] == 0x51
    assert m["model"]["bytes_written"] == 0x78
    assert m["model"]["bytes_changed"] == 1  # solo porque el payload conserva el resto
    assert "0x40" in m["watchdog_offsets_in_block"]


def test_initcom_0x16_accepts_one_byte_at_gate(route, c):
    a = ins(c, 0x4CEC, 0x40)
    assert a[0x4D0E] == "cmp.w r7, #0x20000000"
    assert a[0x4D14] == "ldr r1, [pc, #0x14c]"
    assert a[0x4D16] == "adds r0, r7, r4"
    assert a[0x4D18] == "cmp r0, r1"
    assert a[0x4D1A] == "bls #0x4dc8"
    model = route["initcom"]["command_0x16"]["model"]
    assert model["accepted"] is True and model["bytes_changed"] == 1
    assert model["changed_offsets"] == ["0x50"]
    assert route["initcom"]["command_0x16"]["selective"] is True


def test_initcom_only_exists_in_seton(c):
    assert c.bl_callers(0x4BCA) == [0xECFE]
    assert ins(c, 0xECFC, 4)[0xECFC] == "mov r0, sp"
    assert ins(c, 0xECFC, 4)[0xECFE] == "bl #0x4bca"
    # La tarea COM se crea en Seton y no se alcanza desde On.
    assert 0xECE4 not in {i.operands[0].imm for i in c.dis(0x76CE, 0x100)
                          if i.mnemonic in ("bl", "b.w") and i.operands and i.operands[0].type == arm.ARM_OP_IMM}


def test_t022_t023_window_is_not_darwin_sram(route):
    t = route["t022_t023"]
    assert t["in_bionz_dram"] is True and t["overlaps_darwin_sram"] is False
    assert int(t["window_physical"][0], 16) >= 0x80000000
    assert int(t["window_physical"][1], 16) <= 0xC0000000


def test_volatile_route_is_not_demonstrated(route):
    assert route["verdict"] == "NO"
    assert route["prototype"]["viable"] is False
    assert "0x16" in route["prototype"]["missing_link"]
    assert route["bionz_packet_0x0c"]["gate_not_a_field"] is True


# ---------------------------------------------------------------------------------------------- ciclo de vida y regresión


def test_lifecycle_has_no_gate_consumer_in_recovery_or_power(mech):
    lc = mech["lifecycle"]
    assert lc["reset_initcom_upd_off_have_no_gate_consumer"] is True
    assert lc["on_init_reaches_load"] is True
    assert set(lc["state_mains"]) == {"Init", "Seton", "On", "Exiton", "Off", "Upd"}


def test_regression_with_e24_gate_sites(c):
    # Los 12 consumidores de 0x1fe66 y las listas no cambian con E25.
    assert sorted(c.bl_callers(0x1FE66)) == [0x1F4BA, 0x1F4DE, 0x1F576, 0x1F5A2, 0x1F5A8, 0x1F896,
                                             0x1F908, 0x1FA40, 0x1FE88, 0x1FE90, 0x1FE98, 0x201BC]
    assert c.u32(0x29CF0) == 0x29D0C and c.u32(0x29CF4) == 0x0A


def test_patch_does_not_touch_initcom_watchdog_power_upd_reset(patched):
    _, _, m = patched
    for name in ("initcom", "watchdog", "power_table", "upd_main", "reset", "bootloader_mailbox"):
        reg = next(x for x in m["preserved"]["protected_regions"] if x["name"] == name)
        assert reg["unchanged"] is True
        assert reg["sha256_before"] == reg["sha256_after"]


def test_candidate_is_offline_only(patched):
    _, _, m = patched
    assert m["safety"]["installable"] is False
    assert m["safety"]["recovery_blocker"].startswith("E24-04")
    assert "No instalar" in m["safety"]["warning"]


def test_mss_emitters_are_byte_identical(patched):
    out, _, _ = patched
    original = DARWIN.read_bytes()
    patched_bytes = out.read_bytes()
    # Sitios TX de E24-05f: 0x0b/0x0d/0x15/0x0e/0x10 (api A) y 0x11/0x14 (api B).
    sites = [0x17142, 0x172C4, 0x17308, 0x17428, 0x17530, 0x21284, 0x212AA]
    for site in sites:
        lo, hi = site - BASE, site - BASE + 16
        assert original[lo:hi] == patched_bytes[lo:hi], hex(site)
