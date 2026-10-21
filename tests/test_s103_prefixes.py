"""S103 — prefijos de traza exclusivos de la A6000.

Verifica contra los bytes de av-cam.bin los conteos, las cadenas exactas y las
xrefs PIC de ADC_DEBUG, AVR, ADR, BKID, AVOUT y CAMCORE.
Ver analysis/s103_prefixes/a6000_prefixes.md y .json
"""
import collections
import json
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

DATA = json.loads((ROOT / "analysis" / "s103_prefixes" / "a6000_prefixes.json").read_text())
STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")
PREFIX_RE = re.compile(r"\[([A-Z][A-Z0-9_]{2,})\]")
EXPECTED = {"ADC_DEBUG": 14, "AVR": 2, "ADR": 1, "BKID": 4, "AVOUT": 2, "CAMCORE": 37}


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 400)
    return d[off:end].decode("ascii", "replace")


def count_prefixes(model="A6000"):
    d = data(model)
    cnt = collections.Counter()
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        for mm in PREFIX_RE.finditer(s):
            cnt[mm.group(1)] += 1
    return cnt


def u16(model, addr):
    return struct.unpack_from("<H", data(model), addr - B)[0]


def u32(model, addr):
    return struct.unpack_from("<I", data(model), addr - B)[0]


def pic_target(model, site):
    """Resuelve `ldr rN,[pc,#imm]` (+ `add rN,pc`) y devuelve (destino, registro)."""
    h = u16(model, site)
    if (h & 0xF800) == 0x4800:              # LDR (literal) T1
        rt = (h >> 8) & 7
        lit = ((site + 4) & ~3) + (h & 0xFF) * 4
        val = u32(model, lit)
        for k in range(1, 13):
            a = site + 2 * k
            hh = u16(model, a)
            if (hh & 0xFF78) == 0x4478:     # ADD Rd, PC
                rd = (hh & 7) | ((hh >> 4) & 8)
                if rd == rt:
                    return val + (a + 4), rt
        return None, rt
    if h == 0xF8DF:                         # LDR.W (literal) T2
        h2 = u16(model, site + 2)
        rt = (h2 >> 12) & 0xF
        lit = ((site + 4) & ~3) + (h2 & 0xFFF)
        val = u32(model, lit)
        for k in range(2, 16):
            a = site + 2 * k
            hh = u16(model, a)
            if (hh & 0xFF78) == 0x4478:
                rd = (hh & 7) | ((hh >> 4) & 8)
                if rd == rt:
                    return val + (a + 4), rt
        return None, rt
    return None, None


class S103Prefixes(unittest.TestCase):
    def test_counts_match_s79_and_json(self):
        cnt = count_prefixes()
        self.assertEqual(DATA["counts"], EXPECTED)
        for name, n in EXPECTED.items():
            self.assertEqual(cnt.get(name), n, name)
            self.assertEqual(DATA["prefixes"][name]["count"], n, name)
        self.assertEqual(sum(EXPECTED.values()), 60)

    def test_every_string_matches_bytes(self):
        for name, p in DATA["prefixes"].items():
            for s in p["strings"]:
                addr = int(s["vaddr"], 16)
                self.assertGreaterEqual(addr, B, (name, s["vaddr"]))
                self.assertEqual(cstr(addr).rstrip("\n"), s["text"], (name, s["vaddr"]))
                self.assertIn(f"[{name}]", s["text"], (name, s["vaddr"]))

    def test_every_xref_resolves_to_its_string(self):
        for name, p in DATA["prefixes"].items():
            for s in p["strings"]:
                for site in s["xref_sites"]:
                    target, _ = pic_target("A6000", int(site, 16))
                    self.assertEqual(target, int(s["vaddr"], 16), (name, site, s["vaddr"]))
                for fn in s["functions"]:
                    self.assertGreater(int(fn, 16), B)

    def test_a7s_does_not_have_these_prefixes(self):
        mm = json.loads((ROOT / "analysis" / "s79_modules" / "module_map.json").read_text())
        for name in EXPECTED:
            self.assertNotIn(name, mm["A7S"], name)
            self.assertIn(name, mm["A6000"], name)

    def test_key_anchors_are_byte_exact(self):
        anchors = {
            0x43CE5291: "TSK_ADC",
            0x43CE5315: "boot_exit_adcliro",
            0x43C252B4: "[ACCY][DEBUG][FACTORY]:%d:LANC-AVR Attached",
            0x43C25260: "[ACCY][DEBUG][FACTORY]:%d:AvOut Attached",
            0x43C77AEB: "[SDF] backupId size (BKID_SDF_QTBL_C) is expected %d byte, but %d.)",
            0x43C906B6: "N6Camera7CamCore8RdcImageE",
            0x43CB0B94: "N6Camera7CamCore13SplitRdcImageE",
        }
        for addr, text in anchors.items():
            self.assertEqual(cstr(addr).rstrip("\n"), text, hex(addr))

    def test_s73_five_adj_adc_names(self):
        names = [0x43CE4FC5, 0x43CE4FF2, 0x43CE5021, 0x43CE504E, 0x43CE507A]
        for addr in names:
            self.assertIn("ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_", cstr(addr), hex(addr))
        self.assertEqual(cstr(0x43CE4FC5).rstrip("\n"),
                         "@0ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA")


if __name__ == "__main__":
    unittest.main()
