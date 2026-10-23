"""S346 - tests del carril B: productor del array .bss 0x43e906f4."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s346_array_producer/array_producer.json"
VERIFY = ROOT / "analysis/s346_array_producer/verify_array_producer.py"


class ArrayProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_array_and_slot(self):
        a = self.d["a7s"]
        self.assertEqual(a["array"], "0x43e906f4")
        self.assertTrue(a["array_is_zero_in_image"])
        self.assertEqual(a["occurrences_of_array_literal"], 1)
        self.assertEqual(a["slot_value"], "0x43e906f4")
        self.assertEqual(a["slot_offset_from_got"], "0x00001d00")

    def test_only_two_refs(self):
        self.assertEqual(self.d["a7s"]["slot_refs"], ["0x43705716", "0x4370575e"])
        self.assertEqual(self.d["a6000"]["slot_refs"], ["0x436eb2f6", "0x436eb33e"])
        self.assertTrue(self.d["verdicts"]["references_are_s342_consumers"])

    def test_no_static_writer(self):
        self.assertFalse(self.d["verdicts"]["static_writer"])
        self.assertEqual(self.d["a7s"]["pic_bases_to_array"], [])
        self.assertEqual(self.d["verdicts"]["producer_identity"], "NO_VERIFICADO")

    def test_vtable_slots(self):
        self.assertEqual(self.d["a7s"]["vtable_slots"],
                         {"0x4355f790": "0x2c8", "0x4355f7ac": "0x2cc"})

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)


if __name__ == "__main__":
    unittest.main()
