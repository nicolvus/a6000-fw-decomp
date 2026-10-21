"""S91 — Los submodulos del framework ADF: ADJ, SYSND, GS, FACE, AFNR y CH_SRC.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s91_adf/adf_submodules.md
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


def submod_strings(sub, model="A6000"):
    d = data(model)
    tag = f"[ADF][{sub}]".encode()
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d) if tag in m.group()]


class AdfSubmodules(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(submod_strings("ADJ")), 24)
        self.assertEqual(len(submod_strings("SYSND")), 27)
        self.assertEqual(len(submod_strings("GS")), 2)
        self.assertEqual(len(submod_strings("FACE")), 2)
        self.assertEqual(len(submod_strings("AFNR")), 2)
        self.assertEqual(len(submod_strings("CH_SRC")), 1)

    def test_adj_sets_senser_params(self):
        for addr, param in {
            0x43C26DC1: "SetParamSetMicMode",
            0x43C26DF4: "SetParamSetRecLevel",
            0x43C26E28: "SetParamSetChSource",
            0x43C26E5C: "SetParamSetInputType",
            0x43C26E91: "SetParamSetRecLevelMode",
            0x43C26EC9: "SetParamSetHpMonitor",
            0x43C26EFE: "SetParamSetInputTrim",
            0x43C26F33: "SetParamSetLowCut",
        }.items():
            self.assertIn(param, cstr(addr), hex(addr))
        self.assertIn("AdfSenserCtrl::SetParamSetMicMode", cstr(0x43C26DC1))

    def test_sysnd_has_50_60hz_delays(self):
        joined = "\n".join(submod_strings("SYSND"))
        self.assertIn("m_StartTransDelay60", joined)
        self.assertIn("m_StartTransDelay50", joined)
        self.assertIn("PS ON", joined)
        self.assertIn("m_dummySetOutputSysndDelay", joined)

    def test_gs_path_and_state(self):
        self.assertEqual(cstr(0x43C327D3), "[ADF][GS]START PROC PATH ERR ")
        self.assertEqual(cstr(0x43C327F2), "[ADF][GS]START STATE ERR state : %x")

    def test_face_start_stop(self):
        self.assertEqual(cstr(0x43C32A3B), "[ADF][FACE]StartExecFace")
        self.assertEqual(cstr(0x43C32A54), "[ADF][FACE]StopExecFace")

    def test_afnr(self):
        self.assertEqual(cstr(0x43C32990), "[ADF][AFNR]StartExecAfnr:%x")
        self.assertEqual(cstr(0x43C329AC), "[ADF][AFNR]StopExecAfnr")

    def test_ch_src_avio_mic(self):
        self.assertEqual(cstr(0x43C2E99A), "[ADF][CH_SRC] AvioMicStateStart fifoErr %x")

    def test_adj_matches_dbgcmd_inputpro(self):
        """Los SetParamSet de ADJ son la implementacion de los comandos DBGCMD InputPro (S81)."""
        joined = "\n".join(submod_strings("ADJ"))
        for frag in ("SetParamSetInputType", "SetParamSetInputTrim", "SetParamSetChSource",
                     "SetParamSetRecLevelMode"):
            self.assertIn(frag, joined, frag)


if __name__ == "__main__":
    unittest.main()
