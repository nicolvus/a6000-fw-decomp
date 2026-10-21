"""S79 — Mapa de modulos del firmware av-cam.bin por prefijos de log.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s79_modules/module_map.md
"""
import collections
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")
PREFIX_RE = re.compile(r"\[([A-Z][A-Z0-9_]{2,})\]")


def module_map(model="A6000"):
    d = data(model)
    pref = collections.Counter()
    rng = {}
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        a = B + m.start()
        for mm in PREFIX_RE.finditer(s):
            p = mm.group(1)
            pref[p] += 1
            lo, hi = rng.get(p, (a, a))
            rng[p] = (min(lo, a), max(hi, a))
    return pref, rng


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 160)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


class ModuleMap(unittest.TestCase):
    def test_module_counts(self):
        pref_a6, _ = module_map("A6000")
        pref_a7, _ = module_map("A7S")
        self.assertEqual(len(pref_a6), 348)
        self.assertEqual(len(pref_a7), 277)

    def test_camera_main_submodules(self):
        pref, rng = module_map("A6000")
        expected = {
            "CAMERA_MAIN_YC": 970, "CAMERA_MAIN_SYNC": 429, "CAMERA_MAIN": 135,
            "CAMERA_MAIN_TC": 127, "CAMERA_MAIN_LC": 72, "CAMERA_MAIN_CC": 49,
            "CAMERA_MAIN_IM": 42, "CAMERA_MAIN_FC": 9,
        }
        subs = {k: v for k, v in pref.items() if k.startswith("CAMERA_MAIN")}
        self.assertEqual(len(subs), 8)
        for name, n in expected.items():
            self.assertEqual(subs.get(name), n, name)

    def test_biggest_families(self):
        pref, _ = module_map("A6000")
        for name, n in (("ADF", 1231), ("IMAGING_CAP", 697), ("SDF", 477),
                        ("CAM_IMAGER", 371), ("IDT", 298), ("IDT_OPD", 274),
                        ("VDF", 243), ("CAMERA_SA", 231), ("TRK", 216),
                        ("MOUNT_DEBUG", 132), ("FACE", 70), ("CAM_DMM", 54)):
            self.assertEqual(pref.get(name), n, name)

    def test_submodule_content(self):
        """Cada submódulo tiene una función reconocible en sus cadenas."""
        self.assertIn("api_YC_InitCap", cstr(0x43CA892E))
        self.assertIn("SyncResMgr::Lock", cstr(0x43C9B409))
        self.assertIn("GyroStitScl", cstr(0x43CA7FD4))
        self.assertIn("ExtractCaptureData()", cstr(0x43CA54C8))
        self.assertIn("movie thermal diffTemp", cstr(0x43CA6B32))
        self.assertIn("lc_Movie_DM_AF_Util_getMiniRawAddr", cstr(0x43C9C6F6))
        self.assertIn("Eye data is invalid", cstr(0x43CA6944))

    def test_differential_module_sets(self):
        a6, _ = module_map("A6000")
        a7, _ = module_map("A7S")
        only_a6 = set(a6) - set(a7)
        only_a7 = set(a7) - set(a6)
        for name in ("CAMERA_MAIN_YC", "CAMERA_MAIN_SYNC", "CAMERA_MAIN_LC",
                     "CAMERA_MAIN_CC", "CAMERA_MAIN_FC", "CAMERA_MAIN_IM",
                     "CAMERA_MAIN_TC", "CAMERA_IS"):
            self.assertIn(name, only_a6, name)
        for name in ("APL_PARM", "APL_ESR", "NLAP", "PINCOUNT"):
            self.assertIn(name, only_a7, name)


if __name__ == "__main__":
    unittest.main()
