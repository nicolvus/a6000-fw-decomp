"""S59: bytes A6000 y ejecución offline; ninguna aserción de alcance físico."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis/s59/sol"))
import timing_probe as probe


class TimingProbe(unittest.TestCase):
    def test_binary_identity(self):
        self.assertEqual(probe.binary_sha(),
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")

    def test_accessor_actual_root(self):
        self.assertEqual(probe.accessor(), 0x43E94D04)

    def test_writer_copies_exactly_80_bytes(self):
        for fill in (0, 0xA5):
            with self.subTest(fill=fill):
                result = probe.copy_override(fill)
                self.assertEqual(result["destination"], result["source"])
                self.assertEqual(result["guards"], "cccc")
                self.assertEqual(result["stubbed"], {})

    def test_publish_gate(self):
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                result = probe.publish_override(enabled)
                self.assertEqual(result["published"], result["source"] if enabled else "cc" * 80)
                self.assertEqual(result["stubbed"], {})

    def test_constructor_clears_override(self):
        result = probe.constructor_override()
        self.assertEqual(result["override"], "00" * 80)
        self.assertEqual(result["gate"], 0)
        self.assertEqual(result["stubbed"], {})

    def test_consumer_zero_or_override(self):
        for selector in (0, 1, 2):
            with self.subTest(selector=selector):
                result = probe.consumer_slice(selector)
                self.assertEqual(result["output"], result["source"] if selector else "00" * 24)
                self.assertEqual(result["stubbed"], {})

    def test_snapshot_does_not_confuse_histogram_object(self):
        result = probe.snapshot()
        self.assertEqual(result["clock_word"], 0x12345678)
        self.assertEqual(result["M"], bytes(range(48)).hex())
        self.assertEqual(result["stubbed"], {})

    def test_histogram_writer_has_a_different_object(self):
        result = probe.clock_object_binding()
        self.assertEqual(result["ae_source"], 0x43EAEE84)
        self.assertEqual(result["histogram_object"], 0x43EB121C)
        self.assertNotEqual(result["ae_source"], result["histogram_object"])
        self.assertEqual(result["stubbed"], {})

    def test_vdnum_constructor_range_is_not_a_signed_range(self):
        for raw in (0, 0x2FFF, 0x3000, 0x3001, 0xAFFF, 0xB000, 0xFFFF):
            with self.subTest(raw=raw):
                self.assertEqual(probe.vdnum_slice(raw), max(0, raw - 0x3000))

    def test_synthetic_compatibility_boundaries(self):
        rows = probe.compatibility()
        self.assertTrue(all(r["producer"] == r["host"] for r in rows if r["vd"] == 1 or r["svr"] == 1))
        self.assertTrue(any(r["producer"] != r["host"] for r in rows if r["vd"] > 1 and r["svr"] > 1))
        self.assertTrue(all(r["reachability"] == "NO VERIFICADO" for r in rows))

    def test_host_normalizes_underflow_and_mode_nine(self):
        for n, svr, vd, mode, expected in (
            (0, 4, 3, 0, 0), (1, 1, 2, 0, 0),
            (6, 4, 3, 0, 1), (6, 4, 1, 9, 3), (6, 4, 3, 9, 0),
        ):
            with self.subTest(n=n, svr=svr, vd=vd, mode=mode):
                result = probe.host_slice(n, svr, vd, mode)
                self.assertEqual(result["value"], expected)
                self.assertLessEqual(set(result["stubbed"]), {0x4380FCAC, 0x43902718})


if __name__ == "__main__":
    unittest.main()
