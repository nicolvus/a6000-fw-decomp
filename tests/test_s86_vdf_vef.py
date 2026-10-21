"""S86 — El subsistema del visor: VDF (marco de display) y VEF (visor electronico).

Anclas verificadas contra los bytes del av-cam.bin A6000 (fw3.21).
Ver analysis/s86_vdf_vef/vdf_vef_viewfinder.md
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
    end = d.find(b"\x00", off, off + 250)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def module_strings(mod, model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if m.group().startswith(f"[{mod}]".encode())]


def blob_text(model="A6000"):
    return data(model).decode("latin-1")


class VdfFramework(unittest.TestCase):
    def test_trace_counts(self):
        self.assertEqual(len(module_strings("VDF")), 243)
        self.assertEqual(len(module_strings("VEF")), 149)

    def test_core_classes(self):
        self.assertEqual(cstr(0x43C8221B), "static VDF::VDF_ERR VDF::SubsystemMain::Main()")
        self.assertIn("VDF::SubsystemMain::SendCommandOsal", cstr(0x43C8224A))
        self.assertIn("VDF::SubsystemFactory::ExecCmd", cstr(0x43C83B7F))
        self.assertEqual(cstr(0x43C81367), "N3VDF17SubsystemExportIfE")

    def test_message_framework(self):
        t = blob_text()
        for s in ("VDF::MsgAccessor::GetReceiveCateId()",
                  "VDF::MsgAccessor::GetReceivePayload()",
                  "VDF::MsgAccessor::GetReceiveMsgId()",
                  "VDF::MsgIterator::SendCommandOsal(",
                  "VDF::MsgIterator::SendPinOsal(",
                  "VDF::WaitQueue::Enqueue(",
                  "VDF::WaitQueue::Dequeue("):
            self.assertIn(s, t, s)

    def test_display_and_input_commands(self):
        """Los nombres de clase aparecen en forma RTTI (N3VDF...)."""
        t = blob_text()
        expected = [
            "N3VDF31VdfDisplayCmdSetPanelBrightnessE",
            "N3VDF37VdfDisplayCmdSetPanelColorTemperatureE",
            "N3VDF24VdfDisplayCmdSetParallaxE",
            "N3VDF28VdfDisplayCmdSetDetectExtEvfE",
            "N3VDF31VdfDisplayCmdGetPanelBrightnessE",
            "N3VDF25VdfInputCmdSetShutterMuteE",
            "N3VDF18VdfSrvcCmdSetZebraE",
            "N3VDF22VdfSrvcCmdSetHistogramE",
            "N3VDF21VdfSrvcCmdSetGridLineE",
            "N3VDF14VdfPathSetPathE",
            "N3VDF22VdfPathThroughTransferE",
            "N3VDF20VdfInputCmdUpdateYuvE",
        ]
        missing = [s for s in expected if s not in t]
        self.assertEqual(missing, [], f"faltan: {missing}")

    def test_vph_bridge(self):
        t = blob_text()
        expected = [
            "VDF::VdfDisplayCmdSetPanelOut::VphSetZebraCall",
            "VDF::VdfDisplayCmdSetPanelOut::VphSetPeakingCall",
            "VDF::VdfDisplayCmdSetPanelOut::VphSetPanelDepthCall",
            "N3VDF20VphUpdateYuvFunctionE",
            "N3VDF29DrvCallVphLatestCmdHolderImplE",
        ]
        missing = [s for s in expected if s not in t]
        self.assertEqual(missing, [], f"faltan: {missing}")
        self.assertIn("CallVphUpdateYuv size_x", "\n".join(module_strings("VDF")))
        self.assertIn("vph_set_yuv_mute_immediately ON", "\n".join(module_strings("VDF")))

    def test_adf_ssbi_and_clkctrl_links(self):
        t = blob_text()
        self.assertIn("N3VDF20VdfToAdfYcDataSenderE", t)
        self.assertIn("ssbi_read(%x)", "\n".join(module_strings("VDF")))
        self.assertIn("ssbi_write(%x)", "\n".join(module_strings("VDF")))
        self.assertIn("Backup_read(BKID_UPM_BOOT_CIPA_FLAG)", "\n".join(module_strings("VDF")))
        self.assertIn("CheckUpdateYuvTiming(VDF::SubsystemAccessorIf*", t)
        self.assertIn("N3VDF28HtpVfcMainPerformanceCounterE", t)

    def test_face_frame_link(self):
        """El marco de cara del visor viene del subsistema FC (S71)."""
        t = blob_text()
        expected = [
            "N3VDF29VdfInputCmdUpdateFaceFramePinE",
            "VDF::VDF_ERR UpdateFaceFrameNormal(VDF::MsgAccessorIf*",
            "VDF::VdfFaceFrameUtility::UpdateFaceFrameNormal",
            "N3VDF34VdfSrvcCmdSetFaceFrameCommonDesignE",
        ]
        missing = [s for s in expected if s not in t]
        self.assertEqual(missing, [], f"faltan: {missing}")

    def test_yuv_index_and_memory(self):
        t = blob_text()
        expected = [
            "N3VDF20YuvIndexDoubleBufferE",
            "N3VDF29YuvIndexQfhdMemoryManagerImplE",
            "N3VDF28VfxRgba8888ToYuv422ProcessorE",
            "N3VDF27MirrorSubsystemSynchronizerE",
        ]
        missing = [s for s in expected if s not in t]
        self.assertEqual(missing, [], f"faltan: {missing}")


class VefViewfinder(unittest.TestCase):
    def test_mirror_ids(self):
        self.assertIn("mirror_osal_id=%#x", cstr(0x43C8C36E))
        self.assertIn("my_osal_id=%#x, mirror_osal_id=%#x", cstr(0x43C8C39A))

    def test_modes(self):
        joined = "\n".join(module_strings("VEF"))
        for frag in ("3D Mode", "2D Mode", "INIT Mode", "Invalid mode(Error)!!!"):
            self.assertIn(frag, joined, frag)

    def test_multicast_pause(self):
        joined = "\n".join(module_strings("VEF"))
        for frag in ("Receive InfraMulticast PauseNotify",
                     "Receive InfraMulticast PauseReleaseNotify",
                     "Send InfraMulticast Regist Pause"):
            self.assertIn(frag, joined, frag)

    def test_downconversion(self):
        joined = "\n".join(module_strings("VEF"))
        for frag in ("DOWNCON: PAL 50i50p", "DOWNCON: PAL 25p",
                     "DOWNCON: NTSC 60i60p", "DOWNCON: NTSC 30p24p",
                     "Invalid clk_rate (%d)"):
            self.assertIn(frag, joined, frag)

    def test_effect_cancel_vfc_sync(self):
        joined = "\n".join(module_strings("VEF"))
        self.assertIn("VFC Sync!!!", joined)
        self.assertIn("currentVfc(%d) >= targetVfc(%d)", joined)

    def test_dmm_datarec_work_yc(self):
        """El visor toma prestado el bloque de trabajo YC del datarec."""
        self.assertIn("free DMM_UNITTYPE_DATEREC_WORK_YC", "\n".join(module_strings("VEF")))


if __name__ == "__main__":
    unittest.main()
