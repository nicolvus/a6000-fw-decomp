"""S80 — ZIT: correccion de defectos del sensor (DDC) en el imager.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s80_zit/zit_defect_correction.md
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


def zit_strings(model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if re.search(rb"ZIT|Zit|zit", m.group())]


class ZitSubsystem(unittest.TestCase):
    def test_string_counts(self):
        self.assertEqual(len(zit_strings("A6000")), 118)
        self.assertEqual(len(zit_strings("A7S")), 75)

    def test_class_names(self):
        self.assertEqual(cstr(0x43CF768E), "N6Camera6Imager12ZitMemBufferE")
        self.assertEqual(cstr(0x43CF81A1), "N6Camera6Imager18ZitZphDefectBufferE")
        self.assertEqual(cstr(0x43CF96EF), "N6Camera6Imager21ZitZphLineTableBufferE")

    def test_four_memory_areas(self):
        """El motor trabaja sobre adj / usr / slow / mend."""
        self.assertEqual(cstr(0x43CF7706),
                         "[CAM_IMAGER]: ZIT:: shadowAddr adj:%x usr:%x slow:%x mend:%x")
        self.assertIn("adj:%d usr:%d slow:%d mend:%d", cstr(0x43CF788E))
        self.assertEqual(cstr(0x43CF77F6), "[CAM_IMAGER]: ZIT:: mendBuff: addr%x max%dpt")
        self.assertEqual(cstr(0x43CF7823), "[CAM_IMAGER]: ZIT:: SLOW mendBuff skip")

    def test_read_modes_and_banks(self):
        self.assertIn("<read:%d bank:%d>", cstr(0x43CF7771))
        self.assertIn("readModeIdx error", cstr(0x43CF7F2E))

    def test_sa_bridge(self):
        self.assertEqual(cstr(0x43CFA2A7), "[CAM_IMAGER]: ERROR: ZIT_SaOpen %x")
        self.assertEqual(cstr(0x43CFA2CA), "[CAM_IMAGER]: ERROR: ZIT_SaStart %x")
        self.assertEqual(cstr(0x43CFA2EE), "[CAM_IMAGER]: ERROR: ZIT_SaClose %x")
        self.assertEqual(cstr(0x43CFA312),
                         "__uint16_t Camera::Imager::ZitSaFunctionDriver::ZIT_SaClose()")
        self.assertIn("dmmHandleList is Full", cstr(0x43CF9CD3))
        self.assertIn("CloseFreeZitMMUParam", cstr(0x43CFA210))

    def test_sa_operations(self):
        for addr, frag in {
            0x43CF8BAC: "ZIT Merge:Info ch%01x",
            0x43CFA4B4: "ZIT:: SA CONV_THIN ProcInfo",
            0x43CFA798: "ZIT ConvUnity: ProcInfo",
            0x43CFA929: "ZIT ConvZ1c: ProcInfo",
            0x43CFAD05: "ZIT DET: DetectInfo [ch1]",
            0x43CFADBC: "ZIT DET: DetectInfo [ch4]",
            0x43CFADF9: "ZIT DET: RAWInfo",
            0x43CFAE6E: "ZIT Hist: SA START",
            0x43CFAEF4: "ZIT ZphSA: saParamBuf is shortage",
            0x43CF88EB: "ZitSA_ConvDdc: saParamBuf is shortage",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_zph_buffers(self):
        self.assertIn("ZitZphDefectBuffer::reCalcOffset", cstr(0x43CF81C6))
        self.assertIn("ZitZphDefectBuffer::copyBuff", cstr(0x43CF82A7))
        self.assertIn("convertBackupSaveformat", cstr(0x43CF835F))
        self.assertIn("ZphAdj_Merge_Req", cstr(0x43CF9717))
        self.assertIn("ZphDetSA: unexpected defectKind", cstr(0x43CF97C2))
        self.assertIn("ZphAdj_Det_Req", cstr(0x43CF97F4))

    def test_defect_detection_logs(self):
        self.assertIn("SetZitLog_DetectSequencePre()", cstr(0x43CF7E5F))
        self.assertIn("SetZitLog_MassiveDefectDetectNum()", cstr(0x43CF7EA5))
        self.assertIn("SetZitLog_DefectLvAndPos()", cstr(0x43CF7EF2))
        self.assertIn("DetectControlSW %d is not supported", cstr(0x43CF8C87))

    def test_upper_level_drivers(self):
        self.assertEqual(cstr(0x43CB5FC1),
                         "[CAMERA_MAIN_IM]: ZitDdcDriver: Invalid format. [%d][%d]")
        self.assertEqual(cstr(0x43CA71B6),
                         "[CAMERA_MAIN_IM]: ZitZ1cDriver ch:%d is not exist.")


if __name__ == "__main__":
    unittest.main()
