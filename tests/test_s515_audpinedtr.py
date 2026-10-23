import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis", "s515_audpinedtr")
BASE = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter"
FW = {
    "a6000": os.path.join(BASE, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a7s": os.path.join(BASE, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": os.path.join(BASE, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def count_audpinedtr_strings(path):
    out = subprocess.check_output(["strings", path], text=True)
    return sum(1 for line in out.splitlines() if "[AUDPINEDTR]" in line)


class S515AudpinedtrTests(unittest.TestCase):
    def test_artifacts_exist(self):
        for name in ("ad_strings.json", "ad_xrefs.json", "ad_functions.json", "ad_compare.json"):
            self.assertTrue(os.path.exists(os.path.join(ANALYSIS, name)), name)

    def test_string_artifact_count(self):
        with open(os.path.join(ANALYSIS, "ad_strings.json")) as f:
            data = json.load(f)
        self.assertEqual(len(data["strings"]), 34)

    def test_string_count_matches_binary(self):
        self.assertEqual(count_audpinedtr_strings(FW["a6000"]), 34)

    def test_comparison_a6000_a7s(self):
        with open(os.path.join(ANALYSIS, "ad_compare.json")) as f:
            data = json.load(f)
        self.assertEqual(data["a6000"], 34)
        self.assertEqual(data["a7s"], 34)
        self.assertEqual(data["a6300"], 79)
