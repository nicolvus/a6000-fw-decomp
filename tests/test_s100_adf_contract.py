"""S100 — El contrato de comandos del ADF (firmware) y el canal AdfCh (userland).

Anclas verificadas contra av-cam.bin y libBizFw.so.
Ver analysis/s100_adf_contract/adf_command_contract.md
"""
import collections
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

LIB = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
              "nflasha15_unpacked_unpacked/lib")
STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")


def dbgcmds():
    d = data("A6000")
    out = []
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        mm = re.match(r"^\[ADF\]\[DBGCMD\](\w+) (.*)$", s)
        if mm:
            out.append((B + m.start(), mm.group(1), mm.group(2)))
    return out


def adfch_methods():
    t = (LIB / "libBizFw.so").read_bytes().decode("latin-1")
    return sorted(set(re.findall(r"_ZN17OBJAVBBCBASECLASS5AdfCh\d+(\w+?)E", t)))


class AdfContract(unittest.TestCase):
    def test_ninety_commands(self):
        cmds = dbgcmds()
        self.assertEqual(len(cmds), 90)
        self.assertEqual(len([c for c in cmds if c[2].startswith("SetInput")]), 7)

    def test_command_families(self):
        cnt = collections.Counter(c[1] for c in dbgcmds())
        self.assertEqual(cnt["Input"], 16)
        self.assertEqual(cnt["InputPro"], 8)
        self.assertEqual(cnt["Output"], 9)
        self.assertEqual(cnt["OutputPro"], 3)
        self.assertEqual(cnt["System"], 12)
        self.assertEqual(cnt["SystemSound"], 7)
        self.assertEqual(cnt["Proc"], 19)
        self.assertEqual(cnt["SoundAnalyzer"], 4)
        self.assertEqual(cnt["CPU2"], 4)

    def test_key_commands_exist(self):
        joined = "\n".join(f"{p} {n}" for _, p, n in dbgcmds())
        for frag in ("Input SetInput", "InputPro SetAgcLink", "Output SetOutput",
                     "OutputPro SetHpMonitor", "System ClearMSGQ", "SystemSound SetTable",
                     "Proc SetPath", "Proc SetLinearPhase", "SoundAnalyzer StartGolfShot",
                     "CPU2 ExecTime 60Hz max m/s"):
            self.assertIn(frag, joined, frag)

    def test_adfch_channel_methods(self):
        ms = adfch_methods()
        self.assertEqual(len(ms), 35)
        groups = collections.Counter(m[:3] for m in ms)
        self.assertEqual(groups["Prc"], 8)
        self.assertEqual(groups["Sys"], 4)
        self.assertEqual(groups["InS"], 8)
        self.assertEqual(groups["InP"], 7)
        self.assertEqual(groups["Out"], 8)

    def test_same_vocabulary_on_both_sides(self):
        """Los prefijos Prc/Sys/In/Out existen en firmware y userland."""
        fw = {c[1] for c in dbgcmds()}
        for fam in ("Input", "InputPro", "Output", "OutputPro", "System", "SystemSound", "Proc"):
            self.assertIn(fam, fw, fam)
        ul = {m[:3] for m in adfch_methods()}
        for pre in ("Prc", "Sys", "InS", "InP", "Out"):
            self.assertIn(pre, ul, pre)

    def test_userland_only_methods(self):
        """Metodos de AdfCh sin comando equivalente en el firmware (y al reves)."""
        fw = " ".join(n for _, _, n in dbgcmds())
        ms = adfch_methods()
        for m in ("PrcSetPeakDetect", "PrcSetAudioOutpinMute", "OutSetVolume", "SysSetVolume"):
            self.assertIn(m, ms, m)
        for frag in ("SetPeakDetect", "SetAudioOutpinMute"):
            self.assertNotIn(frag, fw, frag)
        # el firmware expone SetManualGainLink pero el userland no
        self.assertIn("SetManualGainLink", fw)
        self.assertNotIn("InProSetManualGainLink", ms)

    def test_explicit_mapping(self):
        """Correspondencia explicita userland <-> firmware."""
        pairs = {
            "PrcSetPath": "Proc SetPath",
            "SysSetTable": "SystemSound SetTable",
            "InSetInput": "Input SetInput",
            "InProSetAgcLink": "InputPro SetAgcLink",
            "OutSetOutput": "Output SetOutput",
            "OutProSetHpMonitor": "OutputPro SetHpMonitor",
        }
        ms = set(adfch_methods())
        fw = {f"{p} {n}" for _, p, n in dbgcmds()}
        for ul, fwc in pairs.items():
            self.assertIn(ul, ms, ul)
            self.assertIn(fwc, fw, fwc)


if __name__ == "__main__":
    unittest.main()
