"""S87 — Almacenamiento, sistema de archivos y tarjeta de memoria.

Anclas verificadas contra los bytes del av-cam.bin y contra las .so del userland.
Ver analysis/s87_storage/storage_filesystem.md
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
STR_RE = re.compile(rb"[\x09\x20-\x7e]{4,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 220)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def blob_text(path):
    return path.read_bytes().decode("latin-1")


class AvcamStorage(unittest.TestCase):
    def test_external_storage_resource(self):
        """El medio externo es un recurso sincronizado de CAMERA_MAIN_SYNC."""
        for addr, frag in {
            0x43CB3148: "ExternalStorageStart() Error",
            0x43CB317F: "ExternalStorageAcquire() Error",
            0x43CB31B8: "ExternalStorageRelease() Error",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))
        self.assertIn("ExternalStorageStart() Error", cstr(0x43CB4372, "A7S"))

    def test_dcim_path(self):
        self.assertEqual(cstr(0x43CAC566), "DCIM/100MSDCF/DSC%05d.ARW")
        self.assertEqual(cstr(0x43CB022B, "A7S"), "DCIM/100MSDCF/DSC%05d.ARW")
        self.assertEqual(cstr(0x4401EA7F), "DCIM/100MSDCF/DSC00001.ARW")

    def test_psd_bin_only_in_fw321(self):
        """/setting/psd.bin es novedad de la fw3.21 de A6000 (0 en A7S)."""
        self.assertEqual(cstr(0x43CCF2B6), "/setting/psd.bin")
        d7 = data("A7S")
        self.assertEqual(d7.find(b"/setting/psd.bin"), -1)

    def test_movie_file_format(self):
        self.assertEqual(cstr(0x43CA3B3A),
                         "[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d")

    def test_no_exfat_strings_in_firmware(self):
        """Resultado NEGATIVO: el FS no esta implementado en av-cam.bin."""
        d = data("A6000")
        for probe in (b"exFAT", b"EXFAT", b"FAT32", b"CLIP_"):
            self.assertEqual(d.find(probe), -1, probe)


class UserlandStorage(unittest.TestCase):
    def test_fsys_is_the_fat_exfat_driver(self):
        t = blob_text(LIB / "libInfraFsys.so")
        self.assertEqual(t.count("EXFAT"), 51)
        self.assertEqual(t.count("FAT32"), 8)
        for s in ("BPB_Media", "BPB_TotSec16/32", "block size (org)", "block start(org)",
                  "FSYS_ATTRIB_ARCHIVE", "FSYS_ATTRIB_DIRECTORY", "FSYS_ATTRIB_VOLUME",
                  "create UTC Offset", "create time_10ms"):
            self.assertIn(s, t, s)

    def test_obj_has_clip_naming_and_space_forecast(self):
        t = blob_text(LIB / "libObj.so")
        self.assertEqual(t.count("CLIP_"), 13)
        for s in ("forcastUseSizeOnDstDisc", "remainSizeOnDstDisc", "mediaSizeOnDstDisc",
                  "isExistUnsupportedContent", "dubbingProhibitionFactor",
                  "mainJpg", "thumJpg", "publicMakerNote", "secretMakerNote"):
            self.assertIn(s, t, s)

    def test_mpr_has_the_index_model(self):
        t = blob_text(LIB / "libmpr.so")
        for s in ("category folder", "content num", "date num", "entry num",
                  "last date folder", "playlist num", "total mark num",
                  "thumbPictFileModTime", "seekPoint 0x%08x: packLength"):
            self.assertIn(s, t, s)

    def test_same_libraries_in_a7s(self):
        for f in ("libInfraFsys.so", "libObj.so", "libmpr.so"):
            self.assertTrue((LIB / f).exists(), f)
            self.assertTrue((LIB_A7 / f).exists(), f)


if __name__ == "__main__":
    unittest.main()
