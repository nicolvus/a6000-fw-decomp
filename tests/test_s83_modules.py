"""S83 — Los modulos "menores" del firmware, decodificados.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s83_modules/minor_modules.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 200)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def module_strings(mod, model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if m.group().startswith(f"[{mod}]".encode())]


class MinorModules(unittest.TestCase):
    def test_accy_is_uart_accessories(self):
        joined = "\n".join(module_strings("ACCY"))
        self.assertIn("NotifyAttachedUart", joined)
        self.assertIn("NotifyDetached", joined)
        self.assertIn("NotifyUartCommand", joined)
        self.assertIn("NotifyUartResponse", joined)
        self.assertIn("[HW]:AD=%d, ID=%d", joined)

    def test_cam_func_mgr_sync_margins(self):
        self.assertIn("SyncProcMargin[usec]", cstr(0x43CA12F6))
        self.assertIn("HS3@CPU0(IDT)", cstr(0x43CA12F6))
        self.assertIn("HS3@CPU3(RCH)", cstr(0x43CA12F6))
        self.assertIn("SetCapMode:Invalid CapMode", cstr(0x43CAF036))
        self.assertIn("QUEUEING", cstr(0x43CAF077))

    def test_video_encoder_error_codes(self):
        joined = "\n".join(module_strings("ENCOUCSTAT"))
        for frag in ("AVC_ENC_VIDEO_ERR_STATE", "AVC_ENC_VIDEO_ERR_MEMORY",
                     "AVC_ENC_VIDEO_ERR_PARAM", "AVC_ENC_VIDEO_ERR_INDEX"):
            self.assertIn(frag, joined, frag)

    def test_video_encoder_status(self):
        self.assertIn("Pts = 0x%08x EndFlug", cstr(0x43CD680B))
        self.assertIn("paddingAreaLength", cstr(0x43CD6861))
        self.assertIn("Use 2nd Latest Index", cstr(0x43CD68AF))

    def test_enc_seq_ctrl_crank_table(self):
        self.assertIn("[O/U Crank] Table[%d] fR[0x%x] sR[0x%x]", cstr(0x43C4BD2B))
        self.assertIn("FrameRate = %x,SamplingRate = %x", cstr(0x43C4BD5F))
        self.assertIn("[state]0x%x -> 0x%x", cstr(0x43C4BDA2))

    def test_sad_sa_program_headers(self):
        joined = "\n".join(module_strings("SAD"))
        for frag in ("CdcSaPrg Hdr Err", "NmlSaPrg Hdr Err", "RsdSaPrg Hdr Err",
                     "Same Unit Handle Get", "alloc_cnt"):
            self.assertIn(frag, joined, frag)

    def test_panel_backup_and_callbacks(self):
        joined = "\n".join(module_strings("PNL"))
        for frag in ("Backup_read()", "cmd_set_conf_dev", "cmd_set_conf_rev",
                     "cmd_set_conf_cb_NULL", "cmd_set_conf_id"):
            self.assertIn(frag, joined, frag)

    def test_augi_header_fields(self):
        joined = "\n".join(module_strings("AUGI"))
        for frag in ("length", "Reserved2", "end_flag", "PS_flag", "EP_flag"):
            self.assertIn(frag, joined, frag)

    def test_wsx_uses_bsfs(self):
        joined = "\n".join(module_strings("WSX"))
        for frag in ("BSFS INIT", "BSFS SEARCH LOOP ERROR", "BSFS CLOSING ERR",
                     "BsfsWSXClear Err"):
            self.assertIn(frag, joined, frag)

    def test_module_trace_counts(self):
        counts = {m: len(module_strings(m)) for m in
                  ("ACCY", "CAM_FUNC_MGR", "ENCOUCSTAT", "VIDENCSTAT", "ENCSEQCTRL",
                   "SAD", "PNL", "AUGI", "WSX")}
        self.assertEqual(counts["ACCY"], 106)
        self.assertEqual(counts["CAM_FUNC_MGR"], 43)
        self.assertEqual(counts["ENCOUCSTAT"], 49)
        self.assertEqual(counts["VIDENCSTAT"], 70)
        self.assertEqual(counts["ENCSEQCTRL"], 46)
        self.assertEqual(counts["SAD"], 45)
        self.assertEqual(counts["PNL"], 41)
        # AUGI aparece como token 75 veces, pero solo 26 cadenas empiezan por el prefijo
        self.assertEqual(counts["AUGI"], 26)
        self.assertEqual(counts["WSX"], 59)


if __name__ == "__main__":
    unittest.main()
