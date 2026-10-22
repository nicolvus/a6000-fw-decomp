import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s152_imager_descriptor_reads/verify_descriptor_reads.py"
spec = importlib.util.spec_from_file_location("s152_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DescriptorReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_two_matching_entries_decode_to_gap_pointer(self):
        entries = self.data["matching_entries"]
        self.assertEqual([x["entry_fields"]["id_u16_le"] for x in entries],
                         ["0x0030", "0x0030"])
        self.assertEqual([x["entry_fields"]["size_u16_le"] for x in entries], [1, 1])
        self.assertEqual([x["entry_fields"]["address_u32_le"] for x in entries],
                         ["0x43eb0850", "0x43eb0850"])

    def test_table_terminators_and_indexes(self):
        entries = self.data["matching_entries"]
        self.assertEqual([x["target_index"] for x in entries], [32, 6])
        self.assertEqual([x["entry_count_including_terminator"] for x in entries], [68, 59])
        self.assertTrue(all(x["terminator_index"] == x["entry_count_including_terminator"] - 1
                            for x in entries))

    def test_scope_preserves_runtime_unknown(self):
        self.assertIn("does not establish runtime reachability", self.data["scope_limit"])
        self.assertIn("source address", self.data["rea"]["write_effect"])


if __name__ == "__main__":
    unittest.main()
