"""S89 — El modulo IDT/IDT_OPD: mapas de parametros del imager, FOPD e IDTSA.

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s89_idt/idt_opd_maps.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 200)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def module_strings(mod, model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if m.group().startswith(f"[{mod}]".encode())]


class IdtOpdPairing(unittest.TestCase):
    """Cada mensaje del modulo aparece dos veces: [IDT_OPD] y [IDT], contiguas."""

    PAIRS = {
        0x43CF2C2E: "[IDT_OPD]: 4cmap.adrs Err:%X",
        0x43CF2C4B: "[IDT]: 4cmap.adrs Err:%X",
        0x43CF2C64: "[IDT_OPD]: histmap.adrs Err:%X",
        0x43CF2C83: "[IDT]: histmap.adrs Err:%X",
        0x43CF2C9E: "[IDT_OPD]: summap.adrs Err:%X",
        0x43CF2CBC: "[IDT]: summap.adrs Err:%X",
        0x43CF2BF0: "[IDT_OPD]: shade_map.adrs Err:%X",
        0x43CF2C11: "[IDT]: shade_map.adrs Err:%X",
        0x43CF1E45: "[IDT_OPD]: imgmap.adrs Err:%X",
        0x43CF1E63: "[IDT]: imgmap.adrs Err:%X",
        0x43CF1EB5: "[IDT_OPD]: refmap.adrs Err:%X",
        0x43CF1ED3: "[IDT]: refmap.adrs Err:%X",
        0x43CF1E03: "[IDT_OPD]: backImgData.adrs Err:%X",
        0x43CF1E26: "[IDT]: backImgData.adrs Err:%X",
        0x43CF40E0: "[IDT_OPD]: miniRAW Addr  : %08x",
        0x43CF4100: "[IDT]: miniRAW Addr  : %08x",
        0x43CF4545: "[IDT_OPD]: 4cmap:%X",
        0x43CF4559: "[IDT]: 4cmap:%X",
        0x43CF463D: "[IDT_OPD]: msain0:%X",
        0x43CF4652: "[IDT]: msain0:%X",
        0x43CF4663: "[IDT_OPD]: msain1:%X",
        0x43CF4678: "[IDT]: msain1:%X",
        0x43CF4689: "[IDT_OPD]: msaout:%X",
        0x43CF469E: "[IDT]: msaout:%X",
        0x43CF46FF: "[IDT_OPD]: p_backImgData:%X",
        0x43CF471B: "[IDT]: p_backImgData:%X",
        0x43CF47CB: "[IDT_OPD]: refmap:%X",
        0x43CF47E0: "[IDT]: refmap:%X",
    }

    def test_message_pairs(self):
        for addr, text in self.PAIRS.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_trace_counts(self):
        # 297 cadenas empiezan por [IDT] (298 apariciones del token: una va incrustada)
        self.assertEqual(len(module_strings("IDT")), 297)
        self.assertEqual(len(module_strings("IDT_OPD")), 273)


class IdtMaps(unittest.TestCase):
    def test_map_addresses(self):
        for addr, text in {
            0x43CF1E45: "[IDT_OPD]: imgmap.adrs Err:%X",
            0x43CF2C2E: "[IDT_OPD]: 4cmap.adrs Err:%X",
            0x43CF2C64: "[IDT_OPD]: histmap.adrs Err:%X",
            0x43CF2C9E: "[IDT_OPD]: summap.adrs Err:%X",
            0x43CF2BF0: "[IDT_OPD]: shade_map.adrs Err:%X",
            0x43CF48C9: "[IDT_OPD]: Can't Get miniRAW Mem",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_miniraw_is_used_by_lens_calibration_af(self):
        """El miniRAW lo consume el AF hibrido/LC (S75/S71)."""
        self.assertEqual(cstr(0x43C9C8BA),
                         "[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle")

    def test_detection_thresholds(self):
        """Regiones de deteccion calculadas por el IDT (enlace con el modulo de caras)."""
        joined = "\n".join(module_strings("IDT"))
        for frag in ("kido_th[%d].up", "kido_th[%d].dn", "ratio_wak[%d].up",
                     "ratio_wak[%d].rgt", "sel_hist Err", "sel_sum Err", "idealWidth Err"):
            self.assertIn(frag, joined, frag)


class FopdAndSplit(unittest.TestCase):
    def test_fopd_channels(self):
        for addr, text in {
            0x43C91547: "[NSX_OPD]: FOPD_AIF_R0_ERROR:%x",
            0x43C91567: "[NSX_OPD]: FOPD_AIF_W0_ERROR:%x",
            0x43C91587: "[NSX_OPD]: FOPD_AIF_W1_ERROR:%x",
            0x43C915A7: "[NSX_OPD]: FOPD_AIF_W2_ERROR:%x",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_fopd_kick_from_capture(self):
        self.assertEqual(cstr(0x43CADD2D),
                         "[IMAGING_CAP]: StartRdraw_Prelight: KickFOPD error")
        self.assertEqual(cstr(0x43CADD60),
                         "[IMAGING_CAP]: StartRdraw_Read: KickFOPD error")

    def test_sync_resmgr_distributes_idt_fopd_prc(self):
        self.assertIn("[FOPD]r0:", cstr(0x43CA2939))
        self.assertIn("[IDT]r0:", cstr(0x43CA2939))

    def test_idtsa_and_split(self):
        for addr, text in {
            0x43CF3306: "[IDT_OPD]: GetIDTSA Unknown aspect:%d",
            0x43CF332C: "[IDT]: GetIDTSA Unknown aspect:%d",
            0x43CF3538: "[IDT_OPD]: IDTSA Invalid Ch select. %d %d",
            0x43CF3562: "[IDT]: IDTSA Invalid Ch select. %d %d",
            0x43CF5147: "[IDT_OPD]: Illegal FRM mode for IDTSA %d",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))
        joined = "\n".join(module_strings("IDT"))
        for frag in ("Split Coordinate: Async invalid", "Illegal Split cap FOPD Call",
                     "Fatal Not Copiled for Split Cap", "Split Movie Cannot use AIF",
                     "Split Movie Cannot use Insel"):
            self.assertIn(frag, joined, frag)


class VatrNsx(unittest.TestCase):
    def test_vatr(self):
        self.assertEqual(cstr(0x43CF3EC8), "[IDT_OPD]: VATR Error det:%x gle:%x")
        self.assertEqual(cstr(0x43C91609), "[NSX_OPD]: VATR released when moving")
        self.assertIn("IDT_STOP_ERR(VATR)", cstr(0x43C9B5AB))

    def test_nsx_opd(self):
        self.assertEqual(cstr(0x43C915C7), "[NSX_OPD]: FRM set SGC unknown %d")
        self.assertEqual(cstr(0x43C915E9), "[NSX_OPD]: FRM start unknown %d")
        joined = "\n".join(module_strings("NSX_OPD"))
        self.assertIn("IDT AIF illegal address", joined)
        self.assertIn("mask error. total_num", joined)


if __name__ == "__main__":
    unittest.main()
