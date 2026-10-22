import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis", "s512_encoucstat")
BASE = "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter"
FW = {
    "a6000": os.path.join(BASE, "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a7s": os.path.join(BASE, "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
    "a6300": os.path.join(BASE, "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}


def count_enc_strings(path):
    out = subprocess.check_output(["strings", path], text=True)
    return sum(1 for line in out.splitlines() if "[ENCOUCSTAT]" in line)


class S512EncoucstatTests(unittest.TestCase):
    def test_artifacts_exist(self):
        for name in ("enc_strings.json", "enc_xrefs.json", "enc_functions.json", "enc_compare.json"):
            self.assertTrue(os.path.exists(os.path.join(ANALYSIS, name)), name)

    def test_string_artifact_count(self):
        with open(os.path.join(ANALYSIS, "enc_strings.json")) as f:
            data = json.load(f)
        self.assertEqual(len(data), 49)

    def test_functions_artifact(self):
        with open(os.path.join(ANALYSIS, "enc_functions.json")) as f:
            data = json.load(f)
        self.assertEqual(len(data), 29)

    def test_compare_artifact(self):
        with open(os.path.join(ANALYSIS, "enc_compare.json")) as f:
            data = json.load(f)
        self.assertEqual(data["counts"]["a6000"], 49)
        self.assertEqual(data["counts"]["a7s"], 54)
        self.assertEqual(data["counts"]["a6300"], 68)

    @unittest.skipUnless(all(os.path.exists(p) for p in FW.values()), "firmware not present")
    def test_binary_string_counts(self):
        self.assertEqual(count_enc_strings(FW["a6000"]), 49)
        self.assertEqual(count_enc_strings(FW["a7s"]), 54)
        self.assertEqual(count_enc_strings(FW["a6300"]), 68)


if __name__ == "__main__":
    unittest.main()
