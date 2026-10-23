"""S345 - tests del carril B: alcanzabilidad de la aplicacion de mascara."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s345_mask_reachability/mask_reachability.json"
VERIFY = ROOT / "analysis/s345_mask_reachability/verify_mask_reachability.py"


class MaskReachability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_a7s_span(self):
        s = self.d["a7s"]["apply_span"]
        self.assertEqual(s["branches"], [])
        self.assertEqual(s["calls"], ["bl #0x436f618c", "bl #0x436f61f8",
                                      "bl #0x436f60ac"])

    def test_a7s_gate(self):
        s = self.d["a7s"]["second_site"]
        self.assertEqual(s["gate_caller"], "0x436f5aec")
        self.assertIn("0x43ad9b50", s["gate"])

    def test_a6000_span(self):
        s = self.d["a6000"]["apply_span"]
        self.assertEqual(s["branches"], [])
        self.assertEqual(s["calls"], ["bl #0x43ad94d8", "bl #0x436d8bd8"])

    def test_same_ops(self):
        v = self.d["verdicts"]
        self.assertTrue(v["same_two_ops_in_both_models"])
        self.assertFalse(v["mask_application_mode_gated_in_span"])
        self.assertFalse(v["a7s_extra_silent_only_path"])
        self.assertTrue(v["difference_is_data_not_reachability"])

    def test_s51(self):
        self.assertIn("sin cambios", self.d["verdicts"]["s51"])
        self.assertIn("S51", " ".join(self.d["limits"]))

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
