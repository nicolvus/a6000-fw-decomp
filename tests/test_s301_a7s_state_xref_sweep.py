import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s301_a7s_state_xref_sweep"
VERIFY = DIR / "verify_sweep.py"
DATA = DIR / "state_xref_sweep.json"


class A7sStateXrefSweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_coverage_is_complete(self):
        sites = {s["site"] for s in self.data["sites"]}
        self.assertEqual(len(sites), 79)
        self.assertEqual(len(self.data["rea_xrefs"]["0x43f7bce6"]), 16)
        self.assertEqual(len(self.data["rea_xrefs"]["0x440251e4"]), 53)

    def test_gates_have_no_writer(self):
        rows = self.data["gates"]["rows"]
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r["type"] == "READ" for r in rows))
        self.assertEqual(self.data["gates"]["writers"], [])
        self.assertFalse(self.data["verdict"]["writer_plus3"])
        self.assertFalse(self.data["verdict"]["writer_plus6"])

    def test_a7s_specific_write_cluster(self):
        offsets = {a.get("offset") for s in self.data["sites"]
                   for a in s["accesses"] if a["kind"] == "write"}
        # estado base y modo en ambas camaras + cluster propio de la A7S
        self.assertLessEqual(offsets, {None, 2, 0xDE, 0xE6, 0xE8, 0xEA})
        self.assertTrue({0xDE, 0xE6, 0xE8, 0xEA}.issubset(offsets))

    def test_firmware_identity_and_limits(self):
        self.assertEqual(self.data["firmware"]["sha256"],
                         "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e")
        self.assertIn("DMA", self.data["verdict"]["limit"])


if __name__ == "__main__":
    unittest.main()
