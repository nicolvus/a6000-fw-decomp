#!/usr/bin/env python3
"""Unit tests for S618 DET_DIR module analysis."""
import json
import unittest
from pathlib import Path


class TestS618DETDIR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = Path(__file__).parent.parent / "analysis" / "s618_det_dir" / "det_dir.json"
        with open(cls.data_path, "r") as f:
            cls.data = json.load(f)

    def test_trace_count_zero(self):
        self.assertEqual(self.data['traces'], 0)
        self.assertEqual(len(self.data['trace_strings']), 0)

    def test_shutter_line_negative(self):
        self.assertEqual(self.data['shutter_line'], "NEGATIVO ACOTADO")

    def test_related_module(self):
        self.assertEqual(self.data['related_module'], "S617 (CAMERA_DEVICE/DET_DIR)")


if __name__ == "__main__":
    unittest.main()