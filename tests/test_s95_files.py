"""S95 — Los ficheros que la camara lee y escribe (SPICA/PSF/DFE/trazas en /mnt).

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s95_files/file_inventory.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")
PATH_RE = re.compile(r"(/(?:setting|mnt|dev|usr|etc|var|proc)/[A-Za-z0-9_./%\-]*)")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 220)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def all_paths(model="A6000"):
    d = data(model)
    out = {}
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        for mm in PATH_RE.finditer(s):
            out.setdefault(mm.group(1), B + m.start())
    return out


class FileInventory(unittest.TestCase):
    def test_total_and_zones(self):
        p = all_paths()
        self.assertEqual(len(p), 43)
        self.assertEqual(len([x for x in p if x.startswith('/usr/sabin')]), 27)
        self.assertEqual(len([x for x in p if x.startswith('/mnt')]), 11)
        self.assertEqual(len([x for x in p if x.startswith('/setting')]), 1)

    def test_spica_family(self):
        p = all_paths()
        spica = sorted(x for x in p if x.startswith('/usr/sabin/spica'))
        self.assertEqual(len(spica), 22)
        for mode in ("still", "mov", "mov_4k", "mov_interlace", "dualrec", "dualrec_4k"):
            self.assertTrue(any(f"spica_musashi_{mode}_" in x for x in spica), mode)
        self.assertTrue(any(x.endswith("_c_tap_step1.bin") for x in spica))
        self.assertTrue(any(x.endswith("_y_tap_step2.bin") for x in spica))

    def test_psf_and_star_tables(self):
        p = all_paths()
        self.assertIn('/usr/sabin/dcv_psf_table_still.bin', p)
        self.assertIn('/usr/sabin/dcv_psf_table_movie.bin', p)
        self.assertIn('/usr/sabin/dcv_psf_table_movie_4k.bin', p)
        self.assertIn('/usr/sabin/dcv_psf_table_dualrec.bin', p)
        self.assertIn('/usr/sabin/star_kernel_param.bin', p)

    def test_dfe_and_setting(self):
        p = all_paths()
        self.assertIn('/usr/dfe/dfe.bin', p)
        self.assertIn('/setting/psd.bin', p)
        self.assertEqual(cstr(p['/setting/psd.bin']), "/setting/psd.bin")
        self.assertEqual(cstr(p['/usr/dfe/dfe.bin']), "/usr/dfe/dfe.bin")

    def test_ramdisk_traces(self):
        """La camara escribe sus propias trazas en el disco RAM."""
        p = all_paths()
        for f in ('/mnt/FILE_IS_%04x.dat', '/mnt/FILE_TC_COMMON_%04x.dat',
                  '/mnt/lc_mslog_%04x.dat', '/mnt/Mount_ms_log_%03d.dat',
                  '/mnt/cc_ms_log%04x.dat', '/mnt/detect_ms_log%04x.dat',
                  '/mnt/log.bin', '/mnt/YC_FILE%04x.dat',
                  '/mnt/%s.%4d%02d%02d_%02d%02d%02d.dat'):
            self.assertIn(f, p, f)

    def test_timezone_files(self):
        p = all_paths()
        for f in ('/etc/localtime', '/usr/share/zoneinfo', '/usr/share/locale'):
            self.assertIn(f, p, f)

    def test_psd_bin_absent_in_a7s(self):
        self.assertNotIn('/setting/psd.bin', all_paths("A7S"))


if __name__ == "__main__":
    unittest.main()
