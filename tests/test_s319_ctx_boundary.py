import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s319_ctx_boundary/ctx_boundary.json"


class CtxBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_ctx_address(self):
        self.assertEqual(self.d["ctx"]["address"], "0x43ea70a0")
        self.assertEqual(self.d["ctx"]["ctx_plus_8"], "0x43ea70a8")

    def test_counts(self):
        self.assertEqual(len(self.d["ctx"]["sites"]), 40)
        self.assertEqual(len(self.d["ctx"]["sites_ctx8"]), 0)
        self.assertEqual(self.d["ctx"]["classification"]["load"], 31)
        self.assertEqual(self.d["ctx"]["classification"]["store"], 1)

    def test_no_store_to_pointer_fields(self):
        self.assertEqual(self.d["ctx"]["stores_at_offset_0_or_8"], [])
        store = [x for x in self.d["ctx"]["classification_detail"]
                 if x["class"] == "store"]
        self.assertEqual(store[0]["offset"], 68)  # ctx+0x44

    def test_no_absolute_words(self):
        self.assertEqual(self.d["absolute_words_av_cam"], {"ctx": 0, "ctx8": 0})
        self.assertTrue(all(not m["hits"] for m in self.d["sibling_modules"]))

    def test_verdict_is_not_absence_proof(self):
        self.assertEqual(self.d["verdict"], "NO_VERIFICADO")
        text = " ".join(self.d["limits"])
        self.assertIn("memoria compartida", text)
        self.assertIn("S51", text)


if __name__ == "__main__":
    unittest.main()
