"""S77 — Creative Style y balance de blancos (A6000 fw3.21 / A7S fw3.20).

Anclas verificadas contra los bytes del av-cam.bin y contra las .so del userland.
Ver analysis/s77_pp/picture_profile_creative_style.md

Sustituye al borrador del subagente (tabla de Picture Profile inexistente, nombres de
parametro que no estan en el firmware, presets de WB no presentes).
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
STR_RE = re.compile(rb"[\x09\x20-\x7e]{3,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 200)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def blob_text(path):
    return path.read_bytes().decode("latin-1")


class CreativeStyleNames(unittest.TestCase):
    TABLE1 = ["Vivid", "Neutral", "Portrait", "Landscape", "Clear", "Deep", "Light",
              "Sunset", "Nightview", "Autumnleaves", "Real", "Sepia", "Standard"]
    ADDR1 = [0x43CA6702, 0x43CA6709, 0x43CA6712, 0x43CA671C, 0x43CA672B, 0x43CA6732,
             0x43CA6738, 0x43CA673F, 0x43CA6747, 0x43CA6752, 0x43CA6760, 0x43CA6766,
             0x43CA676D]

    def test_first_table_13_entries(self):
        for name, addr in zip(self.TABLE1, self.ADDR1):
            self.assertEqual(cstr(addr), name, hex(addr))

    def test_second_table_12_entries(self):
        """La segunda tabla repite los estilos sin la entrada 'Real'."""
        addrs = [0x43CA678B, 0x43CA6792, 0x43CA679B, 0x43CA67A5, 0x43CA67B4, 0x43CA67BB,
                 0x43CA67C1, 0x43CA67C8, 0x43CA67D0, 0x43CA67DB, 0x43CA67E9, 0x43CA67F0]
        expected = ["Vivid", "Neutral", "Portrait", "Landscape", "Clear", "Deep", "Light",
                    "Sunset", "Nightview", "Autumnleaves", "Sepia", "Standard"]
        for name, addr in zip(expected, addrs):
            self.assertEqual(cstr(addr), name, hex(addr))

    def test_same_styles_in_a7s(self):
        for addr, name in ((0x43CB540E, "Vivid"), (0x43CB5415, "Neutral"),
                           (0x43CB543E, "Deep"), (0x43CB545E, "Autumnleaves"),
                           (0x43CB5453, "Nightview")):
            self.assertEqual(cstr(addr, "A7S"), name, hex(addr))

    def test_picture_profile_names_absent_in_firmware(self):
        """Resultado NEGATIVO verificado: no hay 'CreativeStyle'/'PictureProfile'/params en av-cam."""
        d = data("A6000")
        for probe in (b"CreativeStyle", b"PictureProfile", b"Highlight", b"Saturation",
                      b"Sharpness", b"ColorTone", b"wb_shift"):
            self.assertEqual(d.find(probe), -1, probe)

    def test_wb_preset_names_absent_as_strings(self):
        """Los presets fotograficos de WB NO aparecen como cadenas propias del firmware."""
        d = data("A6000")
        for probe in (b"Daylight", b"Incandescent", b"Fluorescent", b"Cloudy"):
            self.assertEqual(d.find(probe), -1, probe)


class WhiteBalanceBlock(unittest.TestCase):
    def test_wb_strings_are_display_calibration(self):
        """Las cadenas wb_* forman parte del bloque de ajuste de panel (ADJ_CMD, S73)."""
        for addr, text in {
            0x43C76C26: "wb_b_data=%02X ",
            0x43C76C36: "wb_data_tmp=%02X ",
            0x43C76C48: "wb_r_data=%02X ",
            0x43C76C6B: "wb_g_data=%02X ",
            0x43C76DCA: "wb_w_data=%02X, ",
            0x43C76DBB: "wb_mask=%02X, ",
            0x43C76E13: "wb_mask=%02X ",
            0x43C76E21: "wb_w_data=%02X ",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_wb_block_precedes_adj_cmd_block(self):
        """El bloque wb_* esta justo antes de los nombres ADJ_CMD_AVBB_PANELEVF_* (S73)."""
        self.assertEqual(cstr(0x43C76C93), "ADJ_CMD_AVBB_PANELEVF_PANELEVF_ADJ_START")
        self.assertLess(0x43C76C26, 0x43C76C93)


class Userland(unittest.TestCase):
    def test_wrapper_creative_style_symbols(self):
        t = blob_text(LIB / "wrapperCreativeStyle.so")
        for s in ("_ZN20WrapperCreativeStyle16getCreativeStyleEP15ViewBaseProductPNS_22WRAPPER_CREATIVE_STYLE",
                  "_ZN20WrapperCreativeStyle16setCreativeStyleEP15ViewBaseProductNS_22WRAPPER_CREATIVE_STYLEE",
                  "_ZN20WrapperCreativeStyle28convertProcessValueIdToValueEiPNS_22WRAPPER_CREATIVE_STYLEE",
                  "_ZN20WrapperCreativeStyle28convertValueToProcessValueIdENS_22WRAPPER_CREATIVE_STYLEERi",
                  "_ZN21CmnViewProcessDataMgr11getInstanceEP15ViewBaseProduct",
                  "6stella8BitArrayIjE"):
            self.assertIn(s, t, s)

    def test_wrapper_white_balance_symbols(self):
        t = blob_text(LIB / "wrapperWhiteBalance.so")
        for s in ("_ZN19WrapperWhiteBalance15getWhiteBalanceEP15ViewBaseProductPNS_21WRAPPER_WHITE_BALANCEEPi",
                  "_ZN19WrapperWhiteBalance15setWhiteBalanceEP15ViewBaseProductNS_21WRAPPER_WHITE_BALANCEEiii",
                  "_ZN19WrapperWhiteBalance20resetAdjustmentValueEP15ViewBaseProductNS_21WRAPPER_WHITE_BALANC",
                  "_ZN18WrapperSettingUtil10readBackupEP15ViewBaseProductja",
                  "_ZN8ViewBase19requestModelExecuteEPKcmP9ParamList",
                  "_ZN13BackupManager22Bkup_Read_Setting_AttrEiiPv"):
            self.assertIn(s, t, s)

    def test_compensation_libraries_exist(self):
        for f in ("cmnShiftExposureCompensation.so", "cmnShiftFlashCompensation.so",
                  "cmnShiftIris.so", "cmnShiftIso.so", "cmnShiftShutterSpeed.so",
                  "wrapperCreativeStyle.so", "wrapperWhiteBalance.so"):
            self.assertTrue((LIB / f).exists(), f)
        # los nombres sugeridos inicialmente no existen
        self.assertFalse((LIB / "cmnShiftHSV.so").exists())
        self.assertFalse((LIB / "cmnShiftWB.so").exists())

    def test_build_path_identifies_model(self):
        t = blob_text(LIB / "wrapperCreativeStyle.so")
        self.assertIn("141H.DSLR.DM_UUD3", t)
        self.assertIn("Guiengine_131H", t)


if __name__ == "__main__":
    unittest.main()
