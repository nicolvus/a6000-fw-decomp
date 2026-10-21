"""S96 — Modos de captura: drive_mode, CapMode y la tabla 69 -> 14 ShdMode.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s96_modes/capture_modes.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs  # noqa: E402

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.skipdata = True


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 220)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


class DriveMode(unittest.TestCase):
    def test_drive_mode_errors(self):
        for addr, frag in {
            0x43C9397A: "Invalid SetExposure Error!! [drive_mode:%2d]",
            0x43C93A6C: "Invalid Execute Error!! [drive_mode:%2d]",
            0x43C93D30: "Invalid SetRead Error!! [drive_mode:%2d]",
            0x43C94A9F: "GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]",
            0x43C94AFF: "Invalid GetModeParam Error!! [drive_mode:%02x]",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_drive_mode_related_helpers(self):
        self.assertIn("eyePtn", cstr(0x43C92BDE))
        self.assertEqual(cstr(0x43CAE26B), "GetPrelightImagerDriveMode")
        self.assertIn("getDriveModeSizeRatio", cstr(0x43CAE2B7))


class CapModeIds(unittest.TestCase):
    def test_capture_manager_traces(self):
        for addr, fn in {
            0x43CA54C8: "ExtractCaptureData()",
            0x43CA552B: "CaptureInit()",
            0x43CA55A9: "SetReadImageParam()",
            0x43CA5627: "SetNRParam()",
            0x43CA56A5: "SetOPDParam()",
        }.items():
            s = cstr(addr)
            self.assertIn(fn, s, hex(addr))
            self.assertIn("[CapMode:%d]", s, hex(addr))
            self.assertIn("[ExposureID:%d]", s, hex(addr))
            self.assertIn("[ContID:%d]", s, hex(addr))

    def test_frameid_and_bdroseq(self):
        self.assertIn("[FrameID:%d]", cstr(0x43CA54C8))
        self.assertIn("[BDROSeq:%d]", cstr(0x43CA552B))


class ShdModeTable(unittest.TestCase):
    def test_tbb_dispatch(self):
        d = data("A6000")
        ins = [i for i in MD.disasm(d[0x438EF40E - B:0x438EF418 - B], 0x438EF40E)
               if i.mnemonic != ".byte"]
        ops = [(i.address, i.mnemonic, i.op_str) for i in ins]
        self.assertIn((0x438EF40E, "push", "{r0, r1, r4, lr}"), ops)
        self.assertIn((0x438EF410, "cmp", "r3, #0x44"), ops)
        self.assertIn((0x438EF414, "tbb", "[pc, r3]"), ops)

    def test_table_has_69_entries(self):
        d = data("A6000")
        tbl = d[0x438EF418 - B:0x438EF418 - B + 69]
        self.assertEqual(len(tbl), 69)
        self.assertEqual(tbl[0], 0x4B)   # primera entrada (salto relativo)


class NamedModes(unittest.TestCase):
    def test_named_capture_modes(self):
        self.assertEqual(cstr(0x43C7EFFB), "[SDF][CCNR_ENCODE] SDF_RECMODE_STILL_REC")
        self.assertEqual(cstr(0x43CA13BE), "REQ_MOVIE_REC")
        self.assertEqual(cstr(0x43CA15B6), "REPLY_MOVIE_REC")
        self.assertEqual(cstr(0x43CB4BFE), "BURST_CNT")
        self.assertEqual(cstr(0x43CCAF9B), "Burst_")
        self.assertEqual(cstr(0x43C781E4), "MSG_ID_SDF_PANORAMA_CCNR_ENCODE")
        self.assertEqual(cstr(0x43C79FD2), "ApiPanoramaCcnrEncode.cpp")
        self.assertEqual(cstr(0x43C7B926), "ModulePanoramaCcnrEncode.cpp")
        self.assertIn("PanoramaSweepStart", cstr(0x43CAB054))
        self.assertEqual(cstr(0x43CAB088), "still_cnt_panoramaSweep.cpp")
        self.assertEqual(cstr(0x43CA79BA), "lc_BracketAF.cpp")
        self.assertIn("interval(PTM)", cstr(0x43C7A1A5))


if __name__ == "__main__":
    unittest.main()
