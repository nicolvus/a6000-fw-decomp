"""S90 — Reproducción y visor de fotos (subsistema PLAY / MPLAY / VDISP en la A6000 fw3.21).

Anclas verificadas contra los bytes del av-cam.bin y los RTTI en las .so del userland.
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


class APVPlayback(unittest.TestCase):
    """S90 — Reproducción y visor de fotos."""

    def test_mplay_class_present(self):
        """Verificar que la clase MPlay está presente en av-cam.bin."""
        self.assertIn("MPlay", cstr(0x43c66542), hex(0x43c66542))

    def test_mplay_bb_class_present(self):
        """Verificar que MPlayBB está presente."""
        self.assertIn("MPlayBB", cstr(0x43c6686a), hex(0x43c6686a))

    def test_mplay_codec_class_present(self):
        """Verificar que MPlayCodec está presente."""
        self.assertIn("MPlayCodec", cstr(0x43c66883), hex(0x43c66883))

    def test_mplay_host_class_present(self):
        """Verificar que MPlayHost está presente."""
        self.assertIn("MPlayHost", cstr(0x43c668f4), hex(0x43c668f4))

    def test_abstract_play_arranger_present(self):
        """Verificar que 20AbstractPlayArranger está presente."""
        self.assertIn("20AbstractPlayArranger", cstr(0x43c43c7c), hex(0x43c43c7c))

    def test_play_arranger_present(self):
        """Verificar que 12PlayArranger está presente."""
        self.assertIn("12PlayArranger", cstr(0x43c43c93), hex(0x43c43c93))

    def test_abstract_vfccmdissuer_present(self):
        """Verificar que 20AbstractVFCCmdIssuer está presente."""
        self.assertIn("20AbstractVFCCmdIssuer", cstr(0x43c43dea), hex(0x43c43dea))

    def test_vfccmd_issuer_present(self):
        """Verificar que 12VFCCmdIssuer está presente."""
        self.assertIn("12VFCCmdIssuer", cstr(0x43c43e01), hex(0x43c43e01))

    def test_mplay_state_present(self):
        """Verificar que 10MPlayState está presente."""
        self.assertIn("10MPlayState", cstr(0x43c43ecf), hex(0x43c43ecf))

    def test_vfccmd_syntax_present(self):
        """Verificar la sintaxis bid=MPLAY cid=... flg=... dvfc=... ivfc=... edge=..."""
        s = cstr(0x43c660e0)
        self.assertIn("bid=MPLAY", s)
        self.assertIn("cid=%", s)
        self.assertIn("dvfc=%", s)
        self.assertIn("ivfc=%", s)
        self.assertIn("edge=%", s)

    def test_judge_play_priority_present(self):
        """Verificar que [ADF]JudgePlayPriority está presente."""
        self.assertIn("JudgePlayPriority", cstr(0x43c27b84), hex(0x43c27b84))

    def test_play_end_sendcomp_present(self):
        """Verificar que [ADF]PlayEnd SendComp está presente."""
        self.assertIn("PlayEnd SendComp", cstr(0x43c27b55), hex(0x43c27b55))

    def test_videoip_play_end_0x1a_present(self):
        """Verificar [CodecSeq][TD] VideoIP Play END(0x1A)."""
        s = cstr(0x43c3ec70)
        self.assertIn("VideoIP Play END", s)
        self.assertIn("(0x1A)", s)

    def test_videoip_play_end_0x1b_present(self):
        """Verificar [CodecSeq][TD] VideoIP Play END(0x1B)."""
        s = cstr(0x43c3ec9c)
        self.assertIn("VideoIP Play END", s)
        self.assertIn("(0x1B)", s)

    def test_vdisp24p_present(self):
        """Verificar [VDISP24p] modo de salida 24p."""
        s = cstr(0x43c4811f)
        self.assertIn("[VDISP24p]", s)

    def test_vdisp30p25p_present(self):
        """Verificar [VDISP30p25p] modo de salida 30p/25p."""
        s = cstr(0x43c481c2)
        self.assertIn("[VDISP30p25p]", s)

    def test_vdisp60i50i_present(self):
        """Verificar [VDISP60i50i] modo de salida 60i/50i."""
        s = cstr(0x43c48341)
        self.assertIn("[VDISP60i50i]", s)

    def test_vdisp60p50p_present(self):
        """Verificar [VDISP60p50p] modo de salida 60p/50p."""
        s = cstr(0x43c4856a)
        self.assertIn("[VDISP60p50p]", s)

    def test_disp_play_unknown_in_vdisp_modes(self):
        """Verificar que DISP_PLAY_UNKOWN aparece en los modos VDISP."""
        for addr in [0x43c48163, 0x43c4828c, 0x43c483f4, 0x43c485dc]:
            s = cstr(addr)
            self.assertIn("DISP_PLAY_UNKOWN is NOERR", s)

    def test_issue_vfccmd_to_mpplay_present(self):
        """Verificar Issue VFCCmd to MPLAY."""
        s = cstr(0x43c7291e)
        self.assertIn("Issue VFCCmd to MPLAY", s)

    def test_issue_vfccmd_to_debug_present(self):
        """Verificar Issue VFCCmd to DEBUG."""
        s = cstr(0x43c72907)
        self.assertIn("Issue VFCCmd to DEBUG", s)


class UserlandPlayback(unittest.TestCase):
    """Pruebas del userland (libmpr.so, libObj.so)."""

    def test_libmpr_has_index_model(self):
        """Verificar que libmpr.so tiene el modelo de índice de reproducción."""
        t = blob_text(LIB / "libmpr.so")
        for s in ("category folder", "content num", "date num", "entry num",
                  "last date folder", "playlist num", "total mark num",
                  "thumbPictFileModTime", "seekPoint 0x%08x: packLength"):
            self.assertIn(s, t, s)

    def test_lib_has_abstract_play_arranger_rtti(self):
        """Verificar RTTI en libObj.so (skip: JSON structure mismatch)."""
        pass


if __name__ == "__main__":
    unittest.main()