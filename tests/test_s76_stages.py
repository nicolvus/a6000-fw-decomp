"""S76 — Etapas del procesado de captura (Stage_*) y funciones SA asociadas.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s76_stages/stage_pipeline.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x20-\x7e]{5,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 160)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def strings_with(prefix, model="A6000"):
    d = data(model)
    return sorted(B + m.start() for m in STR_RE.finditer(d) if m.group().startswith(prefix.encode()))


class CaptureStages(unittest.TestCase):
    def test_stage_inventory(self):
        """73 nombres Stage_* (clases y ficheros fuente) en el blob."""
        stages = strings_with("Stage_")
        self.assertEqual(len(stages), 73)
        names = [cstr(a) for a in stages]
        for n in ("Stage_Apollo.cpp", "Stage_Develop.cpp", "Stage_FaceDetect.cpp",
                  "Stage_KKNR.cpp", "Stage_OPD.cpp", "Stage_SPICA", "Stage_STAR",
                  "Stage_SoftFocus.cpp", "Stage_TBOX.cpp", "Stage_YKNR",
                  "Stage_Adjust.cpp", "Stage_BOKS.cpp", "Stage_Decomp.cpp",
                  "Stage_Panorama.cpp", "Stage_StillDate.cpp", "Stage_Raw.cpp"):
            self.assertIn(n, names, n)

    def test_key_stage_addresses(self):
        expected = {
            0x43C9EE6C: "Stage_SACC",
            0x43CACF07: "Stage_Panorama.cpp",
            0x43CC6CC6: "Stage_Adjust.cpp",
            0x43CC6E0F: "Stage_Apollo.cpp",
            0x43CC71FA: "Stage_BDRO.cpp",
            0x43CC7569: "Stage_BOKS.cpp",
            0x43CC7DF8: "Stage_Decomp.cpp",
            0x43CC82BE: "Stage_Develop.cpp",
            0x43CC8D9D: "Stage_FaceDetect.cpp",
            0x43CC9329: "Stage_KKNR.cpp",
            0x43CC956D: "Stage_MARBLE.cpp",
            0x43CC9785: "Stage_OPD.cpp",
            0x43CC97B4: "Stage_Orientation.cpp",
            0x43CC990C: "Stage_SPICA",
            0x43CC9DD6: "Stage_STAR",
            0x43CC9F22: "Stage_SoftFocus.cpp",
            0x43CCA086: "Stage_StillDate.cpp",
            0x43CCA36A: "Stage_TBOX.cpp",
            0x43CCA4D9: "Stage_YKNR",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_sa_functions_inventory(self):
        """26 funciones del motor de imagen (SA) usadas por las etapas."""
        sa = {cstr(a) for a in strings_with("sa_func_")}
        self.assertEqual(len(sa), 26)
        for n in ("sa_func_BOKS_start", "sa_func_DECOMP_acquire", "sa_func_SPICA_acquire",
                  "sa_func_STAR_release", "sa_func_YKNR_release", "sa_func_LFNR_init",
                  "sa_func_DUALREC_BAYER_acquire", "sa_func_BDEX_exit"):
            self.assertIn(n, sa, n)

    def test_stage_and_sa_names_correspond(self):
        """Cada familia de etapas tiene su familia de SA homonima."""
        sa = {cstr(a) for a in strings_with("sa_func_")}
        for fam in ("BOKS", "DECOMP", "SPICA", "STAR", "YKNR", "LFNR", "DUALREC_BAYER", "BDEX"):
            self.assertTrue(any(n.startswith("sa_func_" + fam) for n in sa), fam)

    def test_a7s_has_the_same_stage_graph(self):
        """La A7S (fw3.20) tiene las mismas etapas del pipeline."""
        a7s = {cstr(a, "A7S") for a in strings_with("Stage_", "A7S")}
        self.assertGreaterEqual(len(a7s), 60)
        self.assertIn("Stage_Apollo.cpp", a7s)
        self.assertIn("Stage_FaceDetect.cpp", a7s)


if __name__ == "__main__":
    unittest.main()
