"""S70 (reconocimiento) — EIS/gyro: anclas verificadas del subsistema de estabilización.

Solo lectura de bytes del av-cam.bin A6000. No ejecuta firmware.
Ver analysis/s70_is/is_gyro_recon.md.
"""
import re
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

STR_RE = re.compile(rb"[\x20-\x7e]{6,}")


def cstr(addr):
    d = data("A6000")
    off = addr - B
    end = d.find(b"\x00", off, off + 128)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def strings_with(text):
    d = data("A6000")
    return [B + m.start() for m in STR_RE.finditer(d) if text.encode() in m.group()]


class IsGyroAnchors(unittest.TestCase):
    def test_is_prefix_layers(self):
        """Tres capas con prefijo propio: [CAMERA_IS][AS], [CAMERA_IS][EIS], [CAMERA_IS][DIST]."""
        for pref in ("[CAMERA_IS][AS]:", "[CAMERA_IS][EIS]:", "[CAMERA_IS][DIST]:"):
            self.assertTrue(strings_with(pref), pref)

    def test_key_log_addresses(self):
        expected = {
            0x43C98DA6: "[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB (%x)",
            0x43C9A1F3: "[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x",
            0x43C9A2B2: "[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!",
            0x43C9A324: "[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d",
            0x43C9A3A7: "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)",
            0x43CB6EEA: "[CAMERA_MAIN_TC]: JudgeBrkGyro %d",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_is_calibration_file_per_lens(self):
        """El EIS usa un fichero de calibracion por lente: /mnt/FILE_IS_%04x.dat."""
        hits = strings_with("/mnt/FILE_IS_%04x.dat")
        self.assertEqual(len(hits), 1)
        self.assertEqual(cstr(hits[0]), "/mnt/FILE_IS_%04x.dat")

    def test_eis_power_rail(self):
        hits = strings_with("EIS_RC1V_SetPower")
        self.assertGreaterEqual(len(hits), 1)


if __name__ == "__main__":
    unittest.main()
