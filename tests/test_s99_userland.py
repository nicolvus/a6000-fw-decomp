"""S99 — La arquitectura del userland: las capas de libObj.so.

Anclas verificadas contra las .so del userland (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s99_userland/userland_architecture.md
"""
import collections
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
              "nflasha15_unpacked_unpacked/lib")
LIB_A7 = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/"
                 "nflasha15_unpacked_unpacked/lib")
MANG = re.compile(r"_ZN(\d+)([A-Za-z_][A-Za-z0-9_]*)")


def namespaces(path):
    t = path.read_bytes().decode("latin-1")
    ns = collections.Counter()
    for m in MANG.finditer(t):
        n = int(m.group(1))
        nm = m.group(2)[:n]
        if nm:
            ns[nm.split("::")[0]] += 1
    return ns, len(set(re.findall(r"_ZN\d+", t))), path.stat().st_size


class UserlandArchitecture(unittest.TestCase):
    def test_libobj_size_and_symbols(self):
        ns, cls, size = namespaces(LIB / "libObj.so")
        self.assertEqual(size, 17436172)
        self.assertEqual(sum(ns.values()), 2507)
        self.assertEqual(len(ns), 167)

    def test_a7s_is_the_same_architecture(self):
        ns, cls, size = namespaces(LIB_A7 / "libObj.so")
        self.assertEqual(size, 16184848)
        self.assertEqual(len(ns), 168)
        self.assertEqual(sum(ns.values()), 2538)

    def test_layer_namespaces(self):
        ns, _, _ = namespaces(LIB / "libObj.so")
        for name, n in (("MprIf", 318), ("MWF", 241), ("ux", 227), ("AVBIZ", 138),
                        ("OBJAVBBCBASECLASS", 128), ("MprCtrl", 58), ("ViewBase", 53),
                        ("LayoutableWidgetBase", 45), ("InputService", 36), ("UFW", 34),
                        ("AppWidgetBase", 27), ("NetCommonLibrary_", 25), ("GCM_", 24),
                        ("CmnViewMenuData", 23), ("SequenceBase", 23), ("ScalarView", 17)):
            self.assertEqual(ns.get(name), n, name)

    def test_widget_toolkits(self):
        ns, _, _ = namespaces(LIB / "libObj.so")
        for name in ("GEN_GridList", "GEN_Calendar", "GEN_Button", "GEN_Label",
                     "GEN_Balloon", "GEN_EditBox"):
            self.assertIn(name, ns, name)

    def test_key_symbols_exist(self):
        t = (LIB / "libObj.so").read_bytes().decode("latin-1")
        for s in ("_ZN3MWF10ObjMsgList6GetMsgEi",
                  "_ZN2ux4core13GraphicsImage4copyEPvS2_",
                  "_ZN5AVBIZ8UNIVERSE13UActiveObject12SendMsgToAppEPN3MWF6ObjMsgE",
                  "_ZN3UFW11RsrcWrapper13AcquireSingleE",
                  "LayoutableWidgetBase",
                  "C_DataflowInfra_Entry_ImageSizeInfo"):
            self.assertIn(s, t, s)

    def test_net_common_library_smaller_in_a6000(self):
        """La A6000 tiene menos codigo de red que la A7S (10 simbolos menos)."""
        ns6, _, _ = namespaces(LIB / "libObj.so")
        ns7, _, _ = namespaces(LIB_A7 / "libObj.so")
        self.assertEqual(ns6["NetCommonLibrary_"], 25)
        self.assertEqual(ns7["NetCommonLibrary_"], 35)


if __name__ == "__main__":
    unittest.main()
