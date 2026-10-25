"""Comprueba contratos estáticos sin convertir similitud en equivalencia física."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from followup_audit import (
    AVCAM,
    backup_state_source,
    compare_recordstill_callees,
    liro_api_map,
    uipc_route,
)
from recordimage_audit import LIBRARIES, Elf32


def test_kernel_api_slot_is_task_start_and_send_is_osal():
    result = liro_api_map()
    assert result["service_0x3c"] == "sta_tsk"
    assert result["send_0x1d4"] == "osal_snd_msg"
    assert result["copy_destination"] == "*(blob + 0x14) + 0x24"
    assert result["api_entries"] == 209
    assert result["task_id"] == "0x46"
    assert result["task_argument"] == "0x43ea048c"
    assert result["backup_read_0x298"] == "Backup_read"
    assert result["backup_reg_cb_0x2c8"] == "Backup_reg_cb"


def test_backup_source_has_real_state_pointer_key_and_copy_callback():
    result = backup_state_source(AVCAM.read_bytes())
    assert result["index"] == 18
    assert result["state"] == "0x43f72d02"
    assert result["key_both_variants"] == "0x3000b"
    assert result["callback"] == "0x43ae8b7a"
    assert result["callback_operation"] == "memcpy(arg4, arg3, arg2)"
    assert result["effective_size_and_values"] == "NO_VERIFICADO"


def test_user_sender_and_liro_receiver_share_kernel_queue():
    result = uipc_route()
    assert result["send_ioctl"] == "0x80000004"
    assert result["kernel_dispatch_slot"] == 4
    assert result["kernel_helper"] == "__k_4u_snd_msg"
    assert result["queue_low16"] == "0x193"
    assert result["liro_consumer"] == "blocking osal_rcv_msg_tmo"
    assert result["specific_linux_callback_required"] is False


def test_all_recordstill_direct_calls_have_explicit_counterparts():
    result = compare_recordstill_callees()
    assert len(result["calls"]) == 43
    assert len(result["local_pairs"]) == 8
    imports = [row for row in result["calls"] if row["classification"] == "SAME_IMPORT"]
    assert imports
    assert all(row["A6000_symbol"] == row["A7S_symbol"] for row in imports)
    assert result["whole_function_equivalence"] == "NO_VERIFICADO"
    assert result["capture_entry"] == {
        "state": 2, "message": "0x10000005", "check": "0x907ba0",
        "call": "0x90d7e8", "next_state_function": "0x907c94", "next_state": 1,
    }


def test_local_pairs_retain_real_unwind_intervals_instead_of_invented_entries():
    result = compare_recordstill_callees()
    ambiguous = [r for r in result["local_pairs"] if r["A6000"] == "0x915f04"]
    assert ambiguous[0]["A6000_unwind"] == ["0x915c14", "0x915f94"]
    assert ambiguous[0]["classification"] == "LOCAL_CANDIDATE"
    assert Elf32(LIBRARIES["A6000"]).instruction(0x90DE2E).op_str == "#0x90b248"
