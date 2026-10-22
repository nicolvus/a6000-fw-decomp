import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "analysis/s312_cluster_consumers"
VERIFY = DIR / "verify_consumers.py"
DATA = DIR / "consumers.json"


class ClusterConsumers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(VERIFY)], cwd=ROOT, check=True)
        cls.data = json.loads(DATA.read_text())

    def test_six_functions_all_absent(self):
        self.assertEqual(len(self.data["functions"]), 6)
        self.assertTrue(all(f["a6000_hits"] == 0 for f in self.data["functions"]))

    def test_cluster_fields_covered(self):
        fields = {x for r in self.data["site_rows"] for x in r["fields"]}
        for f in ("+0xae", "+0xde", "+0xdf", "+0xe0", "+0xe2", "+0xe4", "+0xe6"):
            self.assertIn(f, fields)

    def test_e4_site_is_the_reload_not_the_spill(self):
        sites = {r["site"]: r for r in self.data["site_rows"]}
        self.assertIn("0x438478ee", sites)
        self.assertNotIn("0x438477f0", sites)


if __name__ == "__main__":
    unittest.main()
