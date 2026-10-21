"""S82 — AutoFraming y etapas de control del pipeline de captura.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s82_autoframing/autoframing_stages.md
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
    end = d.find(b"\x00", off, off + 220)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def hits(pattern, model="A6000"):
    d = data(model)
    return [B + m.start() for m in STR_RE.finditer(d) if pattern in m.group()]


class AutoFraming(unittest.TestCase):
    def test_three_stages_a6000(self):
        self.assertEqual(cstr(0x43CC71A3), "Stage_AutoFraming.cpp")
        self.assertEqual(cstr(0x43CC71B9), "Stage_AutoFraming_ResizeRotate")
        self.assertEqual(cstr(0x43CC71D8), "Stage_AutoFraming_Branch")

    def test_same_stages_in_a7s(self):
        """CORRECCION: la A7S fw3.20 tiene las mismas tres etapas de AutoFraming."""
        self.assertEqual(cstr(0x43CC26AC, "A7S"), "Stage_AutoFraming.cpp")
        self.assertEqual(cstr(0x43CC26C2, "A7S"), "Stage_AutoFraming_ResizeRotate")
        self.assertEqual(cstr(0x43CC26E1, "A7S"), "Stage_AutoFraming_Branch")
        self.assertEqual(len(hits(b"Stage_AutoFraming", "A6000")), 3)
        self.assertEqual(len(hits(b"Stage_AutoFraming", "A7S")), 3)

    def test_framing_force_set_log(self):
        self.assertEqual(cstr(0x43CC7143),
                         "[IMAGING_CAP]: Debug) ResizeRotate Framing size force set: "
                         "offset[%d,%d] size[%d,%d] rotate[%d]")
        self.assertIn("Framing size force set", cstr(0x43CC265B, "A7S"))

    def test_resize_rotate_validation(self):
        for addr, frag in {
            0x43CC6E5F: "ResizeRotate Paramter Error: ImageAreaResize.us_Size_X = %d",
            0x43CC6EF5: "canvas_size.ul_SizeX(%d) < ImageAreaResize.us_Frame_X(%d)",
            0x43CC6FFD: "ResizeRotate Paramter Align Error: ImageAreaResize.us_Frame_X = %d",
            0x43CC70A1: "ResizeRotate Paramter Align Error: ImageAreaResize.us_Size_X = %d",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))


class ControlStages(unittest.TestCase):
    def test_stage_addresses_a6000(self):
        expected = {
            0x43CC7B9C: "Stage_CaComm.cpp",
            0x43CC7BAD: "Stage_CameraHAPI.cpp",
            0x43CACCD6: "Stage_Notify.cpp",
            0x43CAD784: "Stage_WaitControl.cpp",
            0x43C9EE6C: "Stage_SACC",
            0x43CAC363: "Stage_Common.cpp",
            0x43CAC51B: "Stage_DevLater.cpp",
            0x43CAC9F8: "Stage_DualRec.cpp",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_notify_long_exp_is_a_different_string(self):
        """0x43caccb7 es 'Stage_NotifyLongExpNRCapturing'; el .cpp esta en 0x43caccd6."""
        self.assertEqual(cstr(0x43CACCD6), "Stage_Notify.cpp")
        self.assertEqual(cstr(0x43CACCB7), "Stage_NotifyLongExpNRCapturing")
        self.assertEqual(cstr(0x43CB07BB, "A7S"), "Stage_Notify.cpp")

    def test_all_stages_exist_in_a7s(self):
        for addr, text in ((0x43CC2D53, "Stage_CaComm.cpp"), (0x43CC2D83, "Stage_CameraHAPI.cpp"),
                           (0x43CB07BB, "Stage_Notify.cpp"), (0x43CB0F69, "Stage_WaitControl.cpp"),
                           (0x43CB0098, "Stage_Common.cpp"), (0x43CB01EF, "Stage_DevLater.cpp"),
                           (0x43CB0591, "Stage_DualRec.cpp")):
            self.assertEqual(cstr(addr, "A7S"), text, hex(addr))

    def test_sa_relations_by_rodata_adjacency(self):
        """INFERENCIA por proximidad: las trazas de SA vecinas de cada etapa."""
        self.assertIn("sa_func_CONTP_acquire error", cstr(0x43CC7BFA))
        self.assertIn("sa_func_DUALREC_BAYER_acquire", cstr(0x43CAC9C1))
        self.assertIn("sa_func_DUALREC_CLEARVID_start", cstr(0x43CAC867))
        self.assertIn("sa_func_NFLASH_start error", cstr(0x43C9EF73))


if __name__ == "__main__":
    unittest.main()
