"""S73 (reconocimiento) — Protocolo de ajuste ADJ_CMD (panel/EVF/OLED, ADC) y ContrastPlus.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s73_adj/adjust_cmd_recon.md.
"""
import re
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

STR_RE = re.compile(rb"[\x20-\x7e]{6,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 160)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def strings_with(prefix, model="A6000"):
    d = data(model)
    return sorted(B + m.start() for m in STR_RE.finditer(d) if m.group().startswith(prefix.encode()))


def strings_exact(text, model="A6000"):
    """Direcciones de las cadenas cuyo contenido es exactamente `text`."""
    d = data(model)
    needle = text.encode()
    return sorted(B + m.start() for m in STR_RE.finditer(d) if m.group() == needle)


class AdjustCommands(unittest.TestCase):
    def test_avbb_panel_evf_command_inventory(self):
        cmds = strings_with("ADJ_CMD_AVBB_PANELEVF_")
        self.assertEqual(len(cmds), 38)
        self.assertEqual(cstr(cmds[0]), "ADJ_CMD_AVBB_PANELEVF_PANELEVF_ADJ_START")
        self.assertEqual(cstr(cmds[-1]), "ADJ_CMD_AVBB_PANELEVF_PNL_W_WB_G_2BYTE")

    def test_command_groups_present(self):
        for name in ("ADJ_CMD_AVBB_PANELEVF_PNL_W_WB",
                     "ADJ_CMD_AVBB_PANELEVF_PANELEVF_EVF_OLED_CALDAC",
                     "ADJ_CMD_AVBB_PANELEVF_OLED_EVF_THERMISTOR_ADJ_START",
                     "ADJ_CMD_AVBB_PANELEVF_TEST_START_PANELEVF",
                     "ADJ_CMD_AVBB_PANELEVF_PNL_EXTPANEL_DETECT_START",
                     "ADJ_CMD_AVBB_PANELEVF_EVF_TYPE_DET_CONF"):
            self.assertEqual(len(strings_exact(name)), 1, name)

    def test_wb_subblock_address_logs(self):
        self.assertEqual(cstr(0x43C76DDB), "WB_SubB_B_Adrs=%02X, ")
        self.assertEqual(cstr(0x43C76E31), "WB_SubB_R_Adrs=%02X ")
        self.assertEqual(cstr(0x43C76E87), "WB_SubB_G_Adrs=%02X, ")

    def test_handler_structure(self):
        """El manejador lee el ID en +0x18 y el sub-comando en +0x1a (0..0x28)."""
        d = data("A6000")
        ins = list(MD.disasm(d[0x4363524C - B:0x436352C0 - B], 0x4363524C))
        ops = [(i.address, i.mnemonic, i.op_str) for i in ins if i.mnemonic != ".byte"]
        self.assertIn((0x4363527C, "ldrh", "r2, [r6, #0x18]"), ops)   # ID de comando
        self.assertIn((0x4363527E, "movw", "r3, #0x302"), ops)          # ID de referencia
        self.assertIn((0x436352AA, "ldrb", "r3, [r6, #0x1a]"), ops)    # sub-comando
        self.assertIn((0x436352AE, "cmp", "r3, #0x28"), ops)            # rango 0..0x28

    def test_liro_adc_commands(self):
        cmds = strings_with("ADJ_CMD_LIRO_DRIVERS_ADC_")
        self.assertEqual(len(cmds), 4)
        self.assertEqual(cstr(cmds[0]), "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA_ALL")
        self.assertEqual(cstr(cmds[-1]), "ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_SET_DATA")

    def test_contrast_plus(self):
        self.assertEqual(cstr(0x43CC7BC2), "ContrastPlus_Base")
        self.assertEqual(cstr(0x43CC7D5C), "[IMAGING_CAP]: %s: ContrastPlus error")

    def test_names_are_not_in_a_pointer_table(self):
        """Los nombres se cargan uno a uno (literal PIC), no desde una tabla de punteros."""
        import struct
        d = data("A6000")
        pat = struct.pack("<I", 0x43C76C93)
        self.assertEqual(d.find(pat), -1)


if __name__ == "__main__":
    unittest.main()
