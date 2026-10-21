"""S88 — GOLFSHOT (disparo de golf por analisis de sonido) y MOTIONSHOT.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s88_shotmodes/golfshot_motionshot.md
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


def golf_strings(model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if b"GOLFSHOT" in m.group()]


class GolfShot(unittest.TestCase):
    def test_tag_is_nested_in_a6000(self):
        """En la A6000 [GOLFSHOT] va anidado en otros prefijos; en la A7S es prefijo principal."""
        a6 = golf_strings("A6000")
        a7 = golf_strings("A7S")
        self.assertEqual(len(a6), 72)
        self.assertEqual(len(a7), 72)
        self.assertEqual(sum(1 for s in a6 if s.startswith("[GOLFSHOT]")), 0)
        self.assertEqual(sum(1 for s in a7 if s.startswith("[GOLFSHOT]")), 65)

    def test_three_sa_phases(self):
        for addr, frag in {
            0x43CA492F: "[GOLFSHOT]SA_LPF Exec",
            0x43CA4984: "[GOLFSHOT]SA_BGEST Exec",
            0x43CA49D5: "[GOLFSHOT]SA_SSP Exec",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_san_module_commands(self):
        self.assertEqual(cstr(0x43C2C72E), "[SAN]StartGolfShot")
        self.assertEqual(cstr(0x43C2C77A), "[SAN]StopGolfShot")
        self.assertEqual(cstr(0x43C2C792), "[SAN]AnalyzeGolfShot")
        self.assertEqual(cstr(0x43C2C7DD), "[SAN]SetSoundAnalyze")
        self.assertIn("CLAP DETECT SCORE", cstr(0x43CE2F27))
        self.assertIn("deg", cstr(0x43CE2F27))

    def test_adf_debug_commands(self):
        for addr, text in {
            0x43C2B143: "[ADF][DBGCMD]SoundAnalyzer StartGolfShot",
            0x43C2B16C: "[ADF][DBGCMD]SoundAnalyzer StopGolfShot",
            0x43C2B194: "[ADF][DBGCMD]SoundAnalyzer AnalyzeGolfShot",
            0x43C2B1BF: "[ADF][DBGCMD]SoundAnalyzer SetSoundAnalyze",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_alock_buffers(self):
        for addr, frag in {
            0x43CB1915: "ALOCK_ERR: BG_INPUT_IMAGE",
            0x43CB1952: "ALOCK_ERR[%d]: BG_IMAGE",
            0x43CB1988: "ALOCK_ERR[%d]: BG_MASK_IMAGE",
            0x43CB19C3: "ALOCK_ERR[%d]: INPUT_IMAGE[%d]",
            0x43CB1A00: "ALOCK_ERR[%d]: INPUT_LPF_IMAGE",
            0x43CB1A3D: "ALOCK_ERR[%d]: ALPHA_IMAGE",
            0x43CB1A76: "ALOCK_ERR[%d]: KEY_ALPHA_LPF_IMAGE[%d]",
            0x43CB1ABB: "ALOCK_ERR[%d]: SSP_IMAGE[%d]",
            0x43CB1AF6: "ALOCK_ERR[%d]: PRE_KEY_SSP_IMAGE",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_vfc_timing(self):
        self.assertIn("vfc2indx: Shot Timing Transform Error", cstr(0x43CA4A8A))
        self.assertIn("shot_time_vfc error!", cstr(0x43CB18A9))
        self.assertIn("vfc %x vfcSub %x", cstr(0x43C36D0A))

    def test_bgest_uses_jpeg_decoder(self):
        self.assertIn("Seq._BgestPre: JPEG_DEC OPEN OFF", cstr(0x43CB1BA1))


class MotionShot(unittest.TestCase):
    def test_motionshot_removed_in_a6000(self):
        d6, d7 = data("A6000"), data("A7S")
        self.assertEqual(d6.find(b"sa_func_MOTIONSHOT"), -1)
        self.assertGreater(d7.find(b"sa_func_MOTIONSHOT"), -1)
        self.assertEqual(d6.find(b"MOTIONSHOTVIDEO") > 0, True)
        self.assertIn("MOTIONSHOTVIDEO_PARAM_PARAMETER_ERROR", cstr(0x43CE99AB))

    def test_golfshot_sa_api(self):
        for addr, frag in {
            0x43CEDC91: "sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, "
                        "Camera::SaFuncDrv::SSP_START_PARAM*, Camera::SaFuncDrv::SSP_START_MBX*, __uint8_t*)",
            0x43CEDFF6: "sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, "
                        "Camera::SaFuncDrv::BGEST_START_PARAM*, Camera::SaFuncDrv::SA_MBX_0123*, __uint8_t*)",
            0x43CEDF67: "sa_func_GOLFSHOT_release(__uint8_t, __uint16_t, "
                        "Camera::SaFuncDrv::GOLFSHOT_START_PARAM*)",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))


if __name__ == "__main__":
    unittest.main()
