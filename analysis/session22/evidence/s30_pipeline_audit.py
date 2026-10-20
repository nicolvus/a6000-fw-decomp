"""Comprueba las correcciones S30 contra instrucciones y datos originales."""

from __future__ import annotations

import hashlib
import runpy
import struct
import subprocess
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[3]
_helpers = runpy.run_path(str(Path(__file__).with_name("s29_writestill_audit.py")))
LIB = _helpers["LIB"]
elf_word = _helpers["elf_word"]
listing = _helpers["listing"]


class PipelineAudit(unittest.TestCase):
    obj: ClassVar[bytes]
    mpr: ClassVar[bytes]
    camera: ClassVar[bytes]

    @classmethod
    def setUpClass(cls) -> None:
        cls.obj = (LIB / "libObj.so").read_bytes()
        cls.mpr = (LIB / "libmpr.so").read_bytes()
        cls.camera = (LIB.parent.parent / "nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()

    def test_originals(self) -> None:
        for data, digest in (
            (self.obj, "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a"),
            (self.mpr, "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30"),
            (self.camera, "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"),
        ):
            self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_getter_is_not_dma_completion(self) -> None:
        offset = 0x436D6118 - 0x43541000
        self.assertEqual(self.camera[offset:offset + 10].hex(), "024b034a7b4498587047")

    def test_capture_id_service_not_raster(self) -> None:
        # Tabla del receptor: registros de 12 B, no de 16 B.
        offset = 0x44000174 - 0x43541000
        rows = [struct.unpack_from("<3I", self.camera, offset + i * 12) for i in range(35)]
        self.assertIn((0xD008, 0x43AEA99B, 0), rows)
        self.assertTrue(b"GetCaptureID" in self.camera)

    def test_encode_request_and_worker(self) -> None:
        self.assertEqual(elf_word(self.mpr, 0x44F8E4), 0x4000007C)
        self.assertIn("0x429764", listing("libmpr.so", 0x44F8C0, 0x44F8DA))
        self.assertIn("0x4406d4", listing("libmpr.so", 0x42A1DC, 0x42A218))
        self.assertIn("0x717ebc", listing("libmpr.so", 0x44074E, 0x440752))
        self.assertIn("0x718848", listing("libmpr.so", 0x717EBC, 0x717EC8))

    def test_encode_return_is_twelve_bytes(self) -> None:
        self.assertEqual(elf_word(self.mpr, 0x440790), 0x4000007C)
        self.assertEqual(elf_word(self.obj, 0x900940), 0x4000007C)
        code = listing("libObj.so", 0x900974, 0x9009B8)
        self.assertIn("#0xc", code)
        self.assertIn("StructC1", code)
        self.assertIn("0xdbcf8", listing("libObj.so", 0x8FEBA0, 0x8FEBE0))
        self.assertIn("WaitEvent", listing("libObj.so", 0x8FEBA0, 0x8FEBE0))

    def test_encoder_transport_directions(self) -> None:
        self.assertEqual(elf_word(self.mpr, 0x2C0C68), 0x55001F)
        self.assertEqual(elf_word(self.mpr, 0x2C0C14), 0xC70047)
        self.assertEqual(elf_word(self.mpr, 0x2C0E04), 0x2C82F1)
        self.assertIn("osal_snd_msg", listing("libmpr.so", 0x2C0C18, 0x2C0C68))

    def test_converter_sender_receiver_offsets(self) -> None:
        code = listing("libObj.so", 0x920CDA, 0x920D12)
        self.assertIn("EventSenderC1", code)
        self.assertIn("#0x4c]", code)
        self.assertIn("EventReceiverC1", code)
        self.assertIn("#0x50]", code)
        self.assertIn("SetEventReceiver", code)

    def test_avbbc_routes_encode_to_still_encoder(self) -> None:
        self.assertEqual(elf_word(self.obj, 0x26EA9C), 0x55001F)
        self.assertEqual(elf_word(self.obj, 0x26E7CC), 0x550123)
        self.assertEqual(elf_word(self.obj, 0x46BFC4), 0x550123)
        self.assertEqual(elf_word(self.obj, 0x1008230), 0x46BCC5)
        self.assertIn("#0x1500", listing("libObj.so", 0x26E686, 0x26E6A6))
        self.assertIn("0x464200", listing("libObj.so", 0x46BD10, 0x46BD90))
        self.assertEqual(elf_word(self.obj, 0x466300), 0x56000F)

    def test_sdf_command_translation(self) -> None:
        biz = (LIB / "libBizFw.so").read_bytes()
        self.assertEqual(elf_word(biz, 0x4752E), 0x00040304)
        self.assertEqual(elf_word(biz, 0x46344) >> 16, 0x2000)

    def test_encoder_completion_wakes_mpr(self) -> None:
        self.assertEqual(elf_word(self.mpr, 0x719120), 0x71C8A9)
        self.assertEqual(elf_word(self.mpr, 0x2C2D84), 0xA4B14C)
        self.assertEqual(elf_word(self.mpr, 0x2C41BC), 0xA4B14C)
        self.assertEqual(elf_word(self.mpr, 0x71CA50), 0xAD38E8)
        self.assertEqual(elf_word(self.mpr, 0x718B88), 0xAD38E8)
        self.assertIn("0x5fdc84", listing("libmpr.so", 0x71C902, 0x71C91A))

    def test_jpeg_driver_waits_for_registered_safin_callback(self) -> None:
        def word(address: int) -> int:
            return struct.unpack_from("<I", self.camera, address - 0x43541000)[0]

        displacement = struct.unpack("<i", struct.pack("<I", word(0x43937450)))[0]
        self.assertEqual(0x4393724C + displacement, 0x43936B35)
        self.assertEqual(word(0x43BD2DE8), 0xC)
        self.assertEqual(word(0x43BD2DEC), 8)
        self.assertEqual(word(0x43FC4E90), 0x43A9D321)
        code = subprocess.check_output(
            ["llvm-objdump", "-d", "--triple=thumbv7",
             "--start-address=0x43937286", "--stop-address=0x439372a4",
             str(ROOT / "analysis/av-cam-analysis-view.elf")], text=True,
        )
        for target in ("0x439332e4", "0x43933874", "0x43933300"):
            self.assertIn(target, code)

    def test_report_exists(self) -> None:
        self.assertTrue((ROOT / "docs/capture/s30-pipelines-capture-encode.md").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
