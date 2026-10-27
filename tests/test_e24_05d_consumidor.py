"""E24-05d: transporte Darwin→BIONZ de los mensajes mss y su consumo en `av-cam.bin`; lectores de la máscara y los anillos en Darwin.
Informe: docs/capture/e24-05d-consumidor-estado-darwin-bionz.md. Verifican bytes y relaciones, no el texto del informe.
"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("capstone")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/e24_05d"))
sys.path.insert(0, str(ROOT / "scripts/e24_05"))

from bz import AVCAM, Bz
from dwn import DARWIN

if not (AVCAM.exists() and DARWIN.exists()):
    pytest.skip("faltan av-cam.bin o darwin_core.bin", allow_module_level=True)

import hashlib

import transport as t
from dwn import Core


@pytest.fixture(scope="module")
def res():
    return t.main()


def test_binaries_sha(res):
    assert res["sha256_av_cam"] == "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
    assert res["sha256_darwin_core"] == "5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4"
    assert hashlib.sha256(AVCAM.read_bytes()).hexdigest() == res["sha256_av_cam"]


def test_darwin_ids_map_to_caif_rx_handlers(res):
    rx = {r["id"]: r for r in res["caif_rows"] if r["dir"].startswith("Darwin")}
    assert sorted(rx) == [0x0B, 0x0D, 0x0E, 0x10, 0x11, 0x14, 0x15, 0x17]
    assert {k: v["fn_rx"] for k, v in rx.items()} == {
        0x0B: 0x436B8C2C, 0x0D: 0x436B8D18, 0x0E: 0x436B8EF0, 0x10: 0x436B8FE8,
        0x11: 0x436B91C4, 0x14: 0x436B92B0, 0x15: 0x436B8E04, 0x17: 0x436B90D4}
    assert {k: v["trace"] for k, v in rx.items()} == {
        0x0B: 0x121, 0x0D: 0x127, 0x0E: 0x129, 0x10: 0x12E, 0x11: 0x123, 0x14: 0x125, 0x15: 0x137, 0x17: 0x13E}


def test_bionz_to_darwin_rows_have_no_rx_handler(res):
    tx = [r for r in res["caif_rows"] if r["dir"].startswith("BIONZ")]
    assert [r["id"] for r in tx] == [0x0C, 0x0F, 0x12, 0x13, 0x16]
    assert {r["fn_rx"] for r in tx} == {0x43ACAC32} and {r["row_n"] for r in tx} == {1}


def test_id_0c_constructor_is_caif_122():
    b = Bz()
    txt = b.text(0x43ACABAC, 0x40)
    assert "strb.w r3, [sp, #1]" in txt and "strh.w r3, [sp, #4]" in txt  # cls 3, sub 1, len 0x16
    assert "mov.w r0, #0x122" in txt and "bl #0x436ba234" in txt


def test_caif_recv_blocks_forever_and_dispatches_by_sub(res):
    f = res["caif_recv"]
    assert f["tmo_minus1"] and f["rcv_call"] == "0x437dba34" and f["tag"] == "0x1502c7"
    assert f["slot_by_sub"] == {0: 0x20, 2: 0x24, 10: 0x28, 3: 0x2C, 5: 0x30, 12: 0x34, 6: 0x38, 9: 0x3C}
    assert len(f["callers"]) == 8


def test_rcv_syscall_timeout_argument_is_mostly_forever_or_poll(res):
    r = res["rcv_timeouts"]
    assert r["#-1"] == 48 and r["#0"] == 22 and r["#0x3e8"] == 2


def test_stage_waiters_are_called_from_distinct_stage_functions():
    b = Bz()
    exp = {0x438D0B44: [0x438C2978], 0x438D08E8: [0x438C28AC], 0x438D0BE4: [0x438C24BC], 0x438D06E4: [0x438C2800],
           0x438D050C: [0x438CC56C], 0x438D060C: [0x438CC7C8, 0x438CCB0E]}
    for fn, callers in exp.items():
        assert b.bl_callers(fn) == callers


def test_state_block_payload_consumer_reads_fixed_offsets():
    b = Bz()
    txt = b.text(0x438407A0 + 0x64, 0x64)  # 0x43840804..0x43840848: campos de la carga de la subid 5
    for off in ("#0x1f", "#0x19", "#0x18", "#0x1b", "#0x1a", "#0x1d", "#0x1c", "#0x17", "#0x1e"):
        assert f"[r7, {off}]" in txt


def test_darwin_mask_has_no_reader_outside_admission_and_crash_log(res):
    d = res["darwin"]
    assert d["callers_0xd294_mask_getter"] == ["0x6ca0", "0x6ca8", "0x17eba"]
    assert all(0xD098 <= int(a, 16) <= 0xD368 for a in d["mask_literal_users"])


def test_state_block_is_crash_log_snapshot(res):
    d = res["darwin"]
    assert d["callers_0x6ba4_freeze"] == ["0x45b2"] and d["callback_list_0x26d24"] == ["0x69c3", "0x6c79"]
    assert d["callers_0x16bca_ring_copy"] == ["0x6ce0"]
    core = Core()
    assert core.data[0x6B20 - 0x4200:0x6B80 - 0x4200].count(b"logsize") == 2  # "[ERR]KNL logsize", "[ERR]STACK logsize"
    ins = {i.address: i for i in core.dis(0x45A8, 0x10)}
    assert ins[0x45B2].mnemonic == "bl" and ins[0x45B2].op_str == "#0x6ba4" and ins[0x45A8].mnemonic == "push.w"
