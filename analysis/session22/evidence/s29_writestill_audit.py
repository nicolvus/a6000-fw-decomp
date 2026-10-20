"""Audita las aristas de entrada, retorno asíncrono y cierre de WriteStill."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
LIB = ROOT / (
    "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/"
    "nflasha15_unpacked_unpacked/lib"
)


def elf_word(data: bytes, address: int) -> int:
    """Traduce VA mediante PT_LOAD; las secciones de datos no son VA=offset."""
    offset = struct.unpack_from("<I", data, 28)[0]
    size, count = struct.unpack_from("<HH", data, 42)
    for index in range(count):
        kind, file_offset, virtual, _, file_size, _, _, _ = struct.unpack_from(
            "<8I", data, offset + index * size
        )
        if kind == 1 and virtual <= address and address + 4 <= virtual + file_size:
            return struct.unpack_from("<I", data, file_offset + address - virtual)[0]
    raise ValueError(f"VA sin bytes: {address:#x}")


def listing(name: str, start: int, stop: int) -> str:
    return subprocess.check_output(
        ["llvm-objdump", "-d", "--triple=thumbv7-linux-gnueabi",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(LIB / name)],
        text=True,
    )


class WriteStillAudit(unittest.TestCase):
    obj: ClassVar[bytes]
    mpr: ClassVar[bytes]

    @classmethod
    def setUpClass(cls) -> None:
        cls.obj = (LIB / "libObj.so").read_bytes()
        cls.mpr = (LIB / "libmpr.so").read_bytes()

    def test_originals_and_evidence(self) -> None:
        self.assertEqual(hashlib.sha256(self.obj).hexdigest(),
                         "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a")
        self.assertEqual(hashlib.sha256(self.mpr).hexdigest(),
                         "9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30")
        for name in ("s29-write-completion-verified.json", "s29-obj-close.json",
                     "s29-pool-close.json", "s29-pool-writed-path.json",
                     "s29-write-entry-pool-registration.json"):
            data = json.loads((EVIDENCE / name).read_text())
            original = self.obj if data["library"] == "libObj.so" else self.mpr
            self.assertEqual(data["sha256_after"], hashlib.sha256(original).hexdigest())

    def test_entry_and_distinct_terminal_message(self) -> None:
        entry = listing("libObj.so", 0x916306, 0x91633E)
        self.assertIn("0x909a84", entry)
        self.assertEqual(self.obj[0x91631A], 7)
        self.assertEqual(0x91631A + self.obj[0x91631A] * 2, 0x916328)
        self.assertEqual(elf_word(self.obj, 0x90A608), 0x10000004)
        self.assertEqual(elf_word(self.obj, 0x90A60C), 0x10000007)

    def test_callback_registration(self) -> None:
        code = listing("libmpr.so", 0x43F57E, 0x43F590)
        self.assertIn("#0x1020", code)
        self.assertEqual(elf_word(self.mpr, 0x43F5B0), 0x428BAD)
        self.assertEqual(elf_word(self.mpr, 0x81BB50), 0x34B139)
        register = listing("libmpr.so", 0x2D7DB0, 0x2D7DC2)
        for offset in ("#0xc]", "#0x4]", "#0x8]"):
            self.assertIn(offset, register)

    def test_event_66_reaches_real_handler(self) -> None:
        # TBB: byte index 0x66-0x64, relative to PC=0x42bbf2.
        self.assertEqual(self.mpr[0x42BBF2 + 2], 0x14)
        self.assertEqual(0x42BBF2 + self.mpr[0x42BBF2 + 2] * 2, 0x42BC1A)
        self.assertIn("0x441644", listing("libmpr.so", 0x42BC1A, 0x42BC2A))
        self.assertEqual(elf_word(self.mpr, 0x858008 + 0x24), 0x4299D9)
        self.assertEqual(elf_word(self.mpr, 0x858008 + 0x2C), 0x42B9AD)
        self.assertEqual(elf_word(self.mpr, 0x441BA0), 0x40000012)

    def test_pool_mark_is_1007_not_1009(self) -> None:
        self.assertEqual(elf_word(self.obj, 0x101F838), 0x1007)
        self.assertEqual(elf_word(self.obj, 0x101F844), 0x939DD9)
        self.assertEqual(elf_word(self.obj, 0x101F854), 0x1009)
        self.assertEqual(elf_word(self.obj, 0x101F860), 0x939DA9)
        self.assertIn("#0x1007", listing("libObj.so", 0x8FC484, 0x8FC4A0))
        self.assertIn("0x8fc484", listing("libObj.so", 0x8FD738, 0x8FD77E))
        self.assertIn("0x91bb84", listing("libObj.so", 0x910F28, 0x910FE0))
        close = listing("libObj.so", 0x90A2D4, 0x90A440)
        self.assertIn("0x910f28", close)
        self.assertIn("0x90f364", close)

    def test_documented_closure(self) -> None:
        self.assertTrue((ROOT / "docs/capture/s29-writestill-end-to-end.md").is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
