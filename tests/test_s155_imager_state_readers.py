import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s155_imager_state_readers/verify_state_readers.py"
spec = importlib.util.spec_from_file_location("s155_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateReaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_predicates_read_state_byte_zero(self):
        functions = self.data["procedure_ranges"]
        text_a = [i["text"] for i in functions[0]["instructions"]]
        text_b = [i["text"] for i in functions[1]["instructions"]]
        self.assertIn("ldrb r0, [r3]", text_a)
        self.assertIn("ldrb r0, [r3]", text_b)
        self.assertEqual(self.data["slot_values"][0]["value_le"], "0x43f72d02")

    def test_accessor_uses_other_offsets_not_gate_offsets(self):
        text = [i["text"] for i in self.data["procedure_ranges"][2]["instructions"]]
        self.assertTrue(any("#0x4" in line for line in text))
        self.assertTrue(any("#0x1c" in line for line in text))
        self.assertNotIn("strb r2, [r3, #3]", text)
        self.assertNotIn("strb r2, [r3, #6]", text)

    def test_other_store_targets_are_distinct_slots(self):
        self.assertEqual([x["value_le"] for x in self.data["slot_values"]],
                         ["0x43f72d02", "0x43eedb70", "0x43f7c704"])
        self.assertIn("no global writer conclusion", self.data["scope_limit"])


if __name__ == "__main__":
    unittest.main()
