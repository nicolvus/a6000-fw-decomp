import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "analysis/s162_imager_state_event_readers/verify_state_event_readers.py"
spec = importlib.util.spec_from_file_location("s162_verify", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class StateEventReaders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
        cls.data = json.loads(module.OUT.read_text())

    def test_both_sites_are_halfword_reads_of_state_plus_1c(self):
        reads = [r for r in self.data["regions"]
                 if r["address"] in ("0x438d9340", "0x438d937a")]
        self.assertEqual([r["bytes_hex"] for r in reads], ["988b", "988b"])
        self.assertEqual(self.data["state_pointer_slot"]["value_le"], "0x43f72d02")

    def test_results_are_written_to_other_objects(self):
        destinations = [x["value_le"] for x in self.data["other_destination_slots"]]
        self.assertEqual(destinations, ["0x43f7c702", "0x43f7c704"])
        self.assertIn("outside this result", self.data["conclusion_scope"])

    def test_firmware_identity(self):
        self.assertEqual(self.data["firmware_sha256"],
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")


if __name__ == "__main__":
    unittest.main()
