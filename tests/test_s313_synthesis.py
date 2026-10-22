import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/capture/s313-synthesis-carril-b.md"


class Synthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOC.read_text()

    def test_references_all_sessions(self):
        for s in range(300, 313):
            self.assertIn(f"S{s}", self.text)

    def test_open_questions_are_marked(self):
        self.assertIn("NO_VERIFICADO", self.text)
        self.assertIn("vtable", self.text)

    def test_every_row_cites_an_artifact(self):
        rows = [l for l in self.text.splitlines() if re.match(r"\| \d+ \|", l)]
        self.assertGreaterEqual(len(rows), 16)
        for r in rows:
            self.assertTrue(re.search(r"S3\d\d", r), r)

    def test_does_not_claim_physical_mechanism(self):
        self.assertIn("No demuestra", self.text)
        self.assertIn("S51", self.text)


if __name__ == "__main__":
    unittest.main()
