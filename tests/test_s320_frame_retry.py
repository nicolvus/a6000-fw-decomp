import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s320_frame_retry/frames.json"


class FrameRetry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_common_prefix(self):
        self.assertEqual(self.d["common_insn"], 7)
        self.assertEqual(self.d["retry_path"]["entry"], "0x436f25f0")
        self.assertEqual(self.d["plain_path"]["entry"], "0x43ad968a")

    def test_retry_block(self):
        ins = [x["insn"] for x in self.d["extra_block"]]
        self.assertIn("bl #0x43ad92e6", ins)
        self.assertEqual(ins.count("bl #0x43ad9666"), 1)  # el segundo esta tras el bloque
        self.assertIn("cmp r0, #2", ins)

    def test_same_formatter(self):
        retry = [x["insn"] for x in self.d["retry_path"]["insn"]]
        plain = [x["insn"] for x in self.d["plain_path"]["insn"]]
        self.assertIn("bl #0x43ad9666", retry)
        self.assertIn("bl #0x43ad9666", plain)

    def test_a7s_only(self):
        for name in ("retry", "plain", "formatter", "busy"):
            self.assertEqual(self.d["presence"][name]["a6000_hits"], 0)

    def test_limits(self):
        text = " ".join(self.d["limits"])
        self.assertIn("NO_VERIFICADO", text)
        self.assertIn("S51", text)


if __name__ == "__main__":
    unittest.main()
