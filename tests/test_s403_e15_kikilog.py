"""E15/E12: el buzón OSAL 0x0110027c es la cola de kikilog.ko; contra e15_kikilog.json."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parents[1] / "analysis/s403_pendientes/e15_kikilog.json").read_text())


def test_av_cam_emitters_are_log_records():
    em = DATA["av_cam"]["emisores"]
    assert DATA["av_cam"]["palabras_de_pool"] == 13 and len(em) == 13
    msg = {e["send"]: e["campos"] for e in em}
    assert msg["0x437b03bc"] == {"0x0": "0x3", "0x2": "arg", "0x4": "arg", "0x6": "0x22", "0x8": "arg"}
    assert sorted(e["campos"].get("0x6") for e in em if "0x6" in e["campos"]) == ["0x22"] * 6 + ["0x3122"] * 3


def test_receiver_is_kikilog_main_thread():
    k = DATA["kikilog_ko"]
    assert k["main_thread_llamadas"][0] == "osal_rcv_msg_tmo" and "record_log" in k["main_thread_llamadas"]
    assert {"record_acm", "update_wp_status", "osal_snd_msg"} <= set(k["record_log_llamadas"])
    assert k["id_en_data_offsets"] == ["0x7d04"]  # estructura de arranque del hilo
    assert DATA["libObj_refs_ldr"] == 42 and DATA["upm_ko_refs_ldr"] == 51
