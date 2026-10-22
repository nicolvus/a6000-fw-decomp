import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis", "s500_vdf")
BASE = "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter"
FW = {
    "a6000": os.path.join(BASE, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a7s": os.path.join(BASE, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": os.path.join(BASE, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def count_vdf_strings(path):
    out = subprocess.check_output(["strings", path], text=True)
    return sum(1 for line in out.splitlines() if "[VDF]" in line)


class S500VdfTests(unittest.TestCase):
    def test_artifacts_exist(self):
        for name in ("vdf_strings.json", "vdf_xrefs.json", "vdf_functions.json", "vdf_compare.json"):
            self.assertTrue(os.path.exists(os.path.join(ANALYSIS, name)), name)

    def test_string_artifact_count(self):
        with open(os.path.join(ANALYSIS, "vdf_strings.json")) as f:
            data = json.load(f)
        self.assertEqual(len(data), 241)
        self.assertTrue(all("[VDF]" in x["value"] for x in data))

    def test_function_artifact(self):
        with open(os.path.join(ANALYSIS, "vdf_functions.json")) as f:
            data = json.load(f)
        self.assertEqual(len(data), 78)
        top = data[0]
        self.assertEqual(top["address"], "0x4368b874")
        self.assertEqual(top["ref_count"], 12)

    def test_compare_artifact(self):
        with open(os.path.join(ANALYSIS, "vdf_compare.json")) as f:
            data = json.load(f)
        self.assertEqual(data["counts"]["a6000"], 243)
        self.assertEqual(data["counts"]["a7s"], 162)
        self.assertEqual(data["counts"]["a6300"], 162)
        self.assertEqual(data["exclusive_a6000_vs_a7s"], 81)

    @unittest.skipUnless(all(os.path.exists(p) for p in FW.values()), "firmware not present")
    def test_binary_string_counts(self):
        self.assertEqual(count_vdf_strings(FW["a6000"]), 243)
        self.assertEqual(count_vdf_strings(FW["a7s"]), 162)
        self.assertEqual(count_vdf_strings(FW["a6300"]), 162)


if __name__ == "__main__":
    unittest.main()
