"""S98 — libBizFw.so: el orquestador userland y el puente con el framework ADF.

Anclas verificadas contra libBizFw.so (userland fw3.21 y fw3.20) y av-cam.bin.
Ver analysis/s98_bizfw/bizfw_bridge.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

LIB = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
              "nflasha15_unpacked_unpacked/lib")
LIB_A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                 "nflasha15_unpacked_unpacked/lib")
STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")


def blob(name, base=LIB):
    return (base / name).read_bytes().decode("latin-1")


class BizFwBridge(unittest.TestCase):
    def test_library_size(self):
        self.assertEqual((LIB / "libBizFw.so").stat().st_size, 332600)

    def test_three_osal_groups(self):
        t = blob("libBizFw.so")
        for g in ("OSAL_MSGQ_GID_DETECT_FACE", "OSAL_MSGQ_GID_DMM_CTRL", "OSAL_MSGQ_GID_SADRIVER"):
            self.assertIn(g, t, g)

    def test_nine_categories(self):
        t = blob("libBizFw.so")
        cats = sorted(set(re.findall(r"CATEID_[A-Z0-9_]+", t)))
        self.assertEqual(len(cats), 9)
        for c in ("CATEID_PIN", "CATEID_RENDERER", "CATEID_DISPLAY", "CATEID_SYSTEMSOUND",
                  "CATEID_AUDIOPROCESSOR", "CATEID_MIC", "CATEID_MIXER", "CATEID_SPEAKER",
                  "CATEID_EFFECT"):
            self.assertIn(c, cats, c)

    def test_message_ids_and_requests(self):
        t = blob("libBizFw.so")
        ids = sorted(set(re.findall(r"MSG_ID_[A-Z0-9_]+", t)))
        self.assertEqual(ids, ["MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL"])
        reqs = sorted(set(re.findall(r"REQ_[A-Z0-9_]+", t)))
        self.assertEqual(len(reqs), 11)
        for r in ("REQ_DEPOSITE", "REQ_DEPOSIT_MULTIE", "REQ_DESTRUCTE", "REQ_INQUIREE",
                  "REQ_OVERWRITEE", "REQ_PARSEE", "REQ_PEEKE", "REQ_POKEE",
                  "REQ_RAW_PARSEE", "REQ_SHAREE", "REQ_WITHDRAWE"):
            self.assertIn(r, reqs, r)

    def test_adf_channel_mirrors_firmware_commands(self):
        """AdfCh repite el vocabulario de comandos del ADF del firmware (S81)."""
        t = blob("libBizFw.so")
        for sym in ("_ZN17OBJAVBBCBASECLASS5AdfCh10PrcSetPathEh",
                    "_ZN17OBJAVBBCBASECLASS5AdfCh10SysRequestEhhhj",
                    "_ZN17OBJAVBBCBASECLASS5AdfCh10InSetInputEhh",
                    "_ZN17OBJAVBBCBASECLASS5AdfCh11InSetWindNrEhj",
                    "_ZN17OBJAVBBCBASECLASS5AdfCh12OutSetVolumeEh"):
            self.assertIn(sym, t, sym)
        for frag in ("PrcSetPath to ADF", "Snd Msg to ADF"):
            self.assertIn(frag, t, frag)

    def test_ten_destinations(self):
        t = blob("libBizFw.so")
        dests = sorted(set(re.findall(r"Snd Msg to ([A-Z_]+)", t)))
        self.assertEqual(dests, ["ADF", "DETECT", "DMM", "HAPI", "HDMI", "SA", "SDF", "SDI",
                                 "VDF", "VEF"])

    def test_firmware_side_scalar_names(self):
        d = data("A6000")
        txt = d.decode("latin-1")
        # 125 nombres de clase distintos (167 apariciones del token en el binario)
        self.assertEqual(len(set(re.findall(r"NS_SCALAR_INFRA\w+", txt))), 125)
        self.assertIn("N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE", txt)
        self.assertIn("N15NS_SCALAR_INFRA23ScalarInfraSequenceIdleE", txt)

    def test_adf_logs_are_in_userland_not_firmware(self):
        """CORRECCION: las trazas 'PrcSetPath to ADF' estan en el userland, no en av-cam.bin."""
        d = data("A6000")
        self.assertEqual(d.find(b"PrcSetPath to ADF"), -1)
        self.assertIn("PrcSetPath to ADF", blob("libBizFw.so"))

    def test_same_vocabulary_in_a7s(self):
        t7 = blob("libBizFw.so", LIB_A7)
        self.assertEqual(sorted(set(re.findall(r"CATEID_[A-Z0-9_]+", t7))),
                         sorted(set(re.findall(r"CATEID_[A-Z0-9_]+", blob("libBizFw.so")))))
        self.assertIn("MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL", t7)


if __name__ == "__main__":
    unittest.main()
