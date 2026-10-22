import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s154_imager_state_ref/verify_state_ref.py"
spec = importlib.util.spec_from_file_location("s154_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ImagerStateReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_candidate_is_a_got_pointer_load(self):
        self.assertEqual(self.data["slot"]["bytes_hex"], "022df743")
        self.assertEqual(self.data["slot"]["value_le"], "0x43f72d02")
        region = self.data["procedure_ranges"][0]
        lines = [i["text"] for i in region["instructions"]]
        self.assertIn("ldr r0, [r5, r3]", lines)

    def test_function_reads_other_fields_not_gate_offsets(self):
        text = [i["text"] for region in self.data["procedure_ranges"]
                for i in region["instructions"]]
        self.assertIn("ldrb.w r3, [r0, #0x3a]", text)
        self.assertIn("ldrb.w r3, [r0, #0x39]", text)
        self.assertIn("ldrb.w r2, [r0, #0x38]", text)
        self.assertNotIn("ldrb.w r3, [r0, #3]", text)

    def test_rea_edges_are_recorded_as_nonwrites(self):
        self.assertTrue(self.data["scope_limit"].startswith("Only FUN_438363cc"))
        self.assertIn("typed_outgoing_references", self.data["rea_evidence_ids"])


if __name__ == "__main__":
    unittest.main()
