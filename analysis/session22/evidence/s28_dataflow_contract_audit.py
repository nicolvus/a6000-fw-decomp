"""Contrasta registros y contratos Dataflow contra el firmware original."""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[3]
IMAGE = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
BASE = 0x43541000
EVIDENCE = Path(__file__).resolve().parent


def disassemble(path: Path, start: int, stop: int) -> str:
    return subprocess.check_output(
        ["llvm-objdump", "-d", "--triple=thumbv7-linux-gnueabi",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(path)],
        text=True,
    )


def function(filename: str, entry: str) -> str:
    data = json.loads((EVIDENCE / filename).read_text())
    rows = data if isinstance(data, list) else data["functions"]
    return next(row["pseudo_code"] for row in rows if row.get("entry") == entry)


class DataflowContractAudit(unittest.TestCase):
    av: ClassVar[bytes]
    lib: ClassVar[Path]

    @classmethod
    def setUpClass(cls) -> None:
        cls.av = (IMAGE / "nflasha3_unpacked_unpacked/av-cam.bin").read_bytes()
        cls.lib = IMAGE / "nflasha15_unpacked_unpacked/lib"

    def test_original_identity(self) -> None:
        expected = {
            "libObj.so": "8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a",
            "libBizFw.so": "5065aa52ac05d3a7de24945a2c7be65c18394b7c9e02ab605476a0afa8fb8a8e",
            "dataflowInfraFramework.so": "05c0dbb49c9a9519cda65a911a1b5837bb772383a9a181e96468f7b75f5b687b",
        }
        self.assertEqual(hashlib.sha256(self.av).hexdigest(),
                         "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9")
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((self.lib / name).read_bytes()).hexdigest(), digest)

    def test_3_osal_receiver(self) -> None:
        framework = self.lib / "dataflowInfraFramework.so"
        send = disassemble(framework, 0x1BC70, 0x1BD18)
        receive = disassemble(framework, 0x1B968, 0x1BA64)
        self.assertIn("osal_snd_msg@plt", send)
        self.assertIn("osal_rcv_msg_tmo@plt", receive)
        handler = function("s28-osal-callers.json", "4379744c")
        for text in ("0x50004,auStack_1b0,0xffffffff", "sStack_a0 != 0x1000",
                     "uStack_9e == 0", "iVar1 != 5", "0xffffffe0"):
            self.assertIn(text, handler)

    def test_1_imaging_registration(self) -> None:
        table = struct.unpack_from("<5I", self.av, 0x43FF3714 - BASE)
        self.assertEqual(table, (0x43E9DE9C, 0x43E9DE64, 0x43E9DEE0, 0x43E9DF18, 0x43E9DE2C))
        properties = (0x43FF3728, 0x43FF3738, 0x43FF36E4, 0x43FF36F4, 0x43FF3704)
        expected = [(0, 2, index, 0x50004) for index in range(4)] + [(3, 2, 0, 0x50004)]
        for address, value in zip(properties, expected, strict=True):
            self.assertEqual(struct.unpack_from("<4I", self.av, address - BASE), value)
        init = function("s28-imaging-static-init.json", "43797c34")
        self.assertEqual(init.count("FUN_435a97f0("), 5)
        self.assertEqual(struct.unpack_from("<I", self.av, 0x4402005C - BASE)[0], 0x4379744D)
        bind = function("s28-imaging-registration.json", "437970d4")
        self.assertIn("&DAT_43e9d790,0x47,auStack_3c", bind)

    def test_2_peer_pin_semantics(self) -> None:
        # Source rows use index/category/direction/owner; their constructors reorder them.
        for index in range(12):
            self.assertEqual(struct.unpack_from("<4I", self.av, 0x43BB2928 - BASE + index * 16),
                             (index % 6, 0, 1 + index // 6, 0x5A0048))
        for index in range(8):
            self.assertEqual(struct.unpack_from("<4I", self.av, 0x43BD4AE0 - BASE + index * 16),
                             (index % 4, 0, 1 + index // 4, 0x1670464))
        for name, entry, count in (("s28-peer-pin-constructors.json", "436a4b1c", "0xc"),
                                   ("s28-peer-pin-constructors.json", "439a6104", "8")):
            code = function(name, entry)
            self.assertIn("FUN_435a97f0", code)
            self.assertIn(f"iVar2 != {count}", code)
        self.assertIn(b"static VEF::VEF_ERR VEF::SubsystemMain::SendCommandOsal", self.av)
        self.assertIn("ScalarInfraAsyncMain_cpp", function("s28-other-endpoints.json", "439a1864"))

    def test_4_contract_and_corrected_reply_size(self) -> None:
        obj = self.lib / "libObj.so"
        reply = disassemble(obj, 0xA150C8, 0xA150D6)
        self.assertEqual(reply.count("ldm"), 2)
        self.assertEqual(reply.count("stm"), 2)
        getpin = function("s28-getpin-layout.json", "00045a74")
        self.assertIn("&uStack_4c,0x20,&uStack_2c,0x14", getpin)
        connect = function("s28-yc-connect-contract.json", "00153472")
        self.assertIn("param_1[1] = 1", connect)
        self.assertIn("param_1[2] = 0x28", connect)
        self.assertIn("param_2,0x28", function("s28-yc-connect-contract.json", "00a2516c"))
        write = function("s28-writestill-contract.json", "00919a84")
        for text in ("0x10000011", "0x1001,0x28", "0x1007,0x28", "0x6b0", "func_0x0090e0a0"):
            self.assertIn(text, write)
        self.assertNotIn("halt_baddata", write)

    def test_closure_documentation(self) -> None:
        report = ROOT / "docs/capture/s28-osal-pin-contract-closure.md"
        self.assertTrue(report.is_file(), "Falta el cierre técnico de los cuatro puntos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
