"""S81 — ADF: framework de arranque, MSGQ, MMGR y comandos DBGCMD del firmware.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s81_adf/adf_framework.md
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


def adf_strings(model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if m.group().startswith(b"[ADF]")]


class AdfFramework(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(adf_strings("A6000")), 1220)
        self.assertEqual(len(adf_strings("A7S")), 1269)

    def test_dbgcmd_count(self):
        d = data("A6000")
        n = sum(1 for m in STR_RE.finditer(d) if m.group().startswith(b"[ADF][DBGCMD]"))
        self.assertEqual(n, 102)

    def test_boot_sequence(self):
        self.assertEqual(cstr(0x43C26366), "[ADF]BootInit")
        self.assertEqual(cstr(0x43C263C9), "[ADF]BootExit")
        self.assertIn("InitWaitVsync SelectCompo", cstr(0x43C26375))
        self.assertEqual(cstr(0x43C263F6), "[ADF][INIT]AVIO INIT COMP")
        self.assertEqual(cstr(0x43C26411), "[ADF][INIT]AUDIOIP INIT COMP")

    def test_resend_messages(self):
        for addr, frag in {
            0x43C263D8: "INIT Resend MsgqNum",
            0x43C2642F: "Resend header cateId",
            0x43C2648F: "Resend to Adf src",
            0x43C264C1: "Resend No Fifo Data",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_audio_ip_config_types(self):
        for addr, text in {
            0x43C264FA: "[ADF]AUDIO_IP_CONFIG_TYPE_VGS",
            0x43C26518: "[ADF]AUDIO_IP_CONFIG_TYPE_PR",
            0x43C26535: "[ADF]AUDIO_IP_CONFIG_TYPE_MF",
            0x43C26552: "[ADF]AUDIO_IP_CONFIG_TYPE_BANDI_BASEDON_CONS",
            0x43C2657F: "[ADF]AUDIO_IP_CONFIG_TYPE_CONS",
            0x43C2659E: "[ADF]AUDIO_IP_CONFIG_TYPE_BANDI",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_msgq_model(self):
        self.assertEqual(cstr(0x43C26788), "[ADF]MSGQ Set:srcId %08X ,msgId %08X")
        self.assertEqual(cstr(0x43C267D5), "[ADF]MSGQ Get:msgId %08X")
        self.assertIn("SendImmediateComp msgId", cstr(0x43C268A8))
        self.assertIn("ClearAllComp MsgNum", cstr(0x43C2691C))
        self.assertIn("MSGQ_GID_HOTSHOE_INFRA1<-SetInput", cstr(0x43C266E6))
        self.assertIn("MSGQ_GID_HOTSHOE_INFRA1<-SetOutput", cstr(0x43C2670D))

    def test_memmgr_info(self):
        self.assertEqual(cstr(0x43C265CE), "[ADF]MMGR COMM INFO")
        self.assertIn("indexNo, unitType, handle, allocNum, openNum", cstr(0x43C265E3))
        self.assertIn("AdfMemMgrCtrl::SetMemMgrCommResult", cstr(0x43C26652))

    def test_dbgcmd_domains(self):
        for addr, frag in {
            0x43C2A465: "CPU2 ExecTime 60Hz max m/s",
            0x43C2A4CA: "CPU2 ExecTime 48Hz max m/s",
            0x43C2A56F: "System CountMSGQ MsgqNum = %d",
            0x43C2A795: "Proc SetLinearPhase",
            0x43C2AE94: "Input SetInput",
            0x43C2ACB2: "Output SetOutput",
            0x43C2AD78: "OutputPro SetHpOut",
            0x43C2B072: "InputPro SetAgcLink",
            0x43C2B143: "SoundAnalyzer StartGolfShot",
            0x43C2AB8A: "SystemSound SetVol",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_sublane_counts(self):
        d = data("A6000")
        counts = {}
        for m in STR_RE.finditer(d):
            s = m.group().decode("ascii", "replace")
            mm = re.match(r"\[ADF\](?:\[([A-Z0-9_]+)\])?", s)
            if mm:
                counts[mm.group(1) or "(raiz)"] = counts.get(mm.group(1) or "(raiz)", 0) + 1
        self.assertEqual(counts.get("DBGCMD"), 102)
        self.assertEqual(counts.get("ERR"), 70)
        self.assertEqual(counts.get("SYSND"), 27)
        self.assertEqual(counts.get("ADJ"), 24)
        self.assertEqual(counts.get("SAN"), 23)
        self.assertEqual(counts.get("OUT"), 15)


if __name__ == "__main__":
    unittest.main()
