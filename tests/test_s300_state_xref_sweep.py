import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s300_state_xref_sweep"
VERIFY = DIR / "verify_sweep.py"
DATA = DIR / "state_xref_sweep.json"


class StateXrefSweep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # fails if any stored instruction, byte or offset diverges from av-cam.bin
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_coverage_is_complete_for_both_targets(self):
        sites = {s["site"] for s in self.data["sites"]}
        self.assertEqual(len(sites), 67)
        self.assertEqual(self.data["counts"]["total_sites"], 67)
        self.assertEqual(
            {x["address"] for x in self.data["absolute_pointer_literals"]},
            {"0x43ff3248", "0x4401f990"},
        )

    def test_gates_have_readers_and_no_writer(self):
        rows = self.data["gates"]["rows"]
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r["type"] == "READ" for r in rows))
        self.assertEqual(self.data["gates"]["writers"], [])
        self.assertFalse(self.data["verdict"]["writer_plus3"])
        self.assertFalse(self.data["verdict"]["writer_plus6"])

    def test_writers_are_only_state_plus0_and_plus2(self):
        offsets = {a.get("offset") for s in self.data["sites"]
                   for a in s["accesses"] if a["kind"] == "write"}
        self.assertLessEqual(offsets, {None, 2})
        writers = {s["site"] for s in self.data["sites"] if s["class"] == "escritura"}
        self.assertEqual(writers, {"0x43834158", "0x43834188", "0x4383ac8e",
                                   "0x4383ac90", "0x4383afce", "0x4383b30e"})

    def test_scope_limit_is_explicit(self):
        self.assertIn("DMA", self.data["verdict"]["limit"])
        self.assertIn("no por ejecución", self.data["scope_limit"])
        self.assertEqual(self.data["firmware"]["sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
