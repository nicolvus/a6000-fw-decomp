"""S61: comprobaciones contra los bytes reales de av-cam.bin (A6000) y emulación Unicorn del código original."""
import hashlib
import re
import struct
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
for sub in ("analysis/s58", "analysis/s55", "analysis/s61", "analysis/s60/sol"):
    sys.path.insert(0, str(ROOT / sub))
import e3_chain
import e4_producer_a
import trace_payload
from tdis import B, data

SHA = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
BLOB = data("A6000")


def dis(a, b):
    return [(i.address, i.mnemonic, i.op_str) for i in MD.disasm(BLOB[a - B:b - B], a)]


def u32(a):
    return struct.unpack_from("<I", BLOB, a - B)[0]


class Tbh(unittest.TestCase):
    def test_sha(self):
        self.assertEqual(hashlib.sha256(BLOB).hexdigest(), SHA)

    def test_tbh_instruction_and_pc_base(self):
        ins = {a: (m, o) for a, m, o in dis(0x43806A00, 0x43806A08)}
        self.assertEqual(ins[0x43806A04], ("tbh", "[pc, r2, lsl #1]"))
        # en Thumb PC = dirección de la instrucción + 4 (tabla inmediatamente posterior)
        base = 0x43806A04 + 4
        targets = {i: base + 2 * struct.unpack_from("<H", BLOB, base - B + 2 * i)[0] for i in range(12)}
        self.assertEqual((targets[4], targets[10]), (0x43806C28, 0x43806D06))
        self.assertEqual({str(k): hex(v) for k, v in targets.items()}, trace_payload.probe()["case_targets"])

    def test_wrong_base_lands_before_handler(self):
        # con la base antigua (-4) el destino cae en la instrucción anterior al manejador real
        for good in (0x43806C28, 0x43806D06):
            self.assertEqual(dis(good, good + 2)[0][1], "ldr")
            self.assertNotEqual(dis(good - 4, good - 2)[0][1:], dis(good, good + 2)[0][1:])

    def test_handlers_call_expected_functions(self):
        expect = {3: [0x43B00FE6, 0x43B00FA4], 4: [0x43B00DAC, 0x43B00D94, 0x438065FC],
                  9: [0x43B00F62, 0x43B00F22], 10: [0x43B00DAC, 0x43B00CD0, 0x43B00D94, 0x43806590],
                  0: [0x43B01026]}
        tg = {i: 0x43806A08 + 2 * struct.unpack_from("<H", BLOB, 0x43806A08 - B + 2 * i)[0] for i in range(12)}
        ends = sorted(set(tg.values()) | {0x43806DC4, 0x43806DCC, 0x43806E38})
        for case, want in expect.items():
            end = min(x for x in ends if x > tg[case])
            got = [int(o[1:], 16) for _, m, o in dis(tg[case], end) if m == "bl"]
            for fn in want:
                self.assertIn(fn, got, f"caso {case}")


class ProducersAB(unittest.TestCase):
    def test_a_gate_and_stores(self):
        gate = [(m, o) for a, m, o in dis(0x437AB502, 0x437AB510)]
        self.assertEqual(gate[0][0], "ldr"); self.assertIn(("movs", "r1, #6"), gate)
        self.assertIn(("ldrb", "r0, [r5, #0xd]"), gate); self.assertIn(("bl", "#0x43aeb0cc"), gate)
        self.assertEqual(dis(0x437AB50E, 0x437AB510)[0][1], "cbnz")
        self.assertEqual([(m, o) for _, m, o in dis(0x43AEB0CC, 0x43AEB0D4)][:2], [("asrs", "r0, r1"), ("and", "r0, r0, #1")])
        st = [o for _, m, o in dis(0x437AB516, 0x437AB540) if m.startswith("strh")]
        self.assertEqual(len(st), 12)

    def test_a_emulation_gate_bit6(self):
        for g0d, runs in ((0x00, True), (0xBF, True), (0x40, False), (0xFF, False)):
            r = e4_producer_a.run(g0d, 0x1234, 0x5678)
            if runs:
                self.assertEqual(r, [(0x1234, 0x5678)] * 6)
            else:
                self.assertIsNone(r)

    def test_b_gate_and_sources(self):
        head = [(m, o) for _, m, o in dis(0x43AECBEC, 0x43AECBFA)]
        self.assertIn(("ldrb.w", "r3, [r3, #0x3a]"), head); self.assertIn(("cmp", "r3, #1"), head)
        srcs = sorted(int(re.search(r"#(0x[0-9a-f]+)\]", o).group(1), 16)
                      for _, m, o in dis(0x43AECC00, 0x43AECC3E) if m == "ldrh.w")
        self.assertEqual(srcs, [0x48, 0x4A, 0x4C, 0x4E, 0x50, 0x52, 0x54, 0x56, 0x5C, 0x5E])
        self.assertEqual(u32(0x43AECC50 - 0) & 0, 0)  # solo comprueba legibilidad
        self.assertEqual(dis(0x43AECC50, 0x43AECC54)[0][1:], ("bl", "#0x437a5a6c"))

    def test_stage_3a_writers(self):
        zero = dis(0x437AA032, 0x437AA03E)
        self.assertEqual([(m, o) for _, m, o in zero][:2], [("movs", "r3, #0"), ("ldr", "r2, [r4]")])
        self.assertEqual(dis(0x437AA03C, 0x437AA040)[0][1:], ("strb.w", "r3, [r2, #0x3a]"))
        clear = [(m, o) for _, m, o in dis(0x437A9B92, 0x437A9BA4)]
        self.assertIn(("movs", "r1, #6"), [(m, o) for _, m, o in dis(0x437A9B8A, 0x437A9B8C)])
        self.assertIn(("ldrb", "r0, [r6, #0xd]"), clear); self.assertIn(("strb.w", "r2, [r3, #0x3a]"), clear)
        self.assertEqual(dis(0x437AA952, 0x437AA95A)[-1][1:], ("strb.w", "r2, [r7, #0x3a]"))

    def test_p0_writes_b_source_fields(self):
        stores = {int(re.search(r"#(0x[0-9a-f]+)\]", o).group(1), 16)
                  for _, m, o in dis(0x43861ED0, 0x438621BC) if m.startswith("strh") and "[r4," in o}
        for f in e3_chain.FIELDS:
            self.assertIn(f, stores)
        for a in (0x43862BC4, 0x43863668):
            self.assertEqual(dis(a, a + 4)[0][1:], ("bl", "#0x43861ed0"))

    def test_obj8_is_copy_of_obj_plus_2cc(self):
        ins = [(m, o) for _, m, o in dis(0x43AECE6E, 0x43AECE98)]
        self.assertIn(("add.w", "r1, r5, #0x2cc"), ins)
        self.assertIn(("mov.w", "r2, #0x244"), ins)
        self.assertIn(("ldr", "r0, [r4, #8]"), ins)           # destino = p[2] (= obj8)
        self.assertEqual(dis(0x4379FC20, 0x4379FC22)[0][1], "ldr")   # 0x4379fc20: base de objetos, paso 0xf20
        self.assertIn(("mov.w", "r0, #0xf20"), [(m, o) for _, m, o in dis(0x4379FC22, 0x4379FC26)])

    def test_accessor_is_obj_plus_e20(self):
        self.assertEqual([(m, o) for _, m, o in dis(0x43AE8504, 0x43AE8510)][:3],
                         [("push", "{r3, lr}"), ("bl", "#0x437876dc"), ("add.w", "r0, r0, #0xe20")])


class SixthPair(unittest.TestCase):
    def test_table_pointer_setters_and_bk4(self):
        self.assertEqual(dis(0x437AD3B0, 0x437AD3B2)[0][1:], ("str", "r3, [r2]"))
        got = 0x437AD3AA + 4 + 0x871B36
        self.assertEqual((u32(got + 0x3D8), u32(got + 0x381C)), (0x43E95CD0, 0x43E95E10))
        entry = e3_chain.bk4_entry()
        self.assertEqual(len(entry), 232)
        self.assertEqual(entry[:18], b"\x01" * 18); self.assertEqual(entry[18:36], b"\x37" * 18)
        pairs = struct.unpack_from("<36H", entry, 0x36)
        self.assertEqual(pairs, (0x2EA0, 0x6028) * 18)
        self.assertEqual(entry[0x36 + 72:], bytes(len(entry) - 0x36 - 72))

    def test_backup_files_agree(self):
        import glob

        from bk4 import BK4
        d = e3_chain.BK.parent
        raws = set()
        for p in glob.glob(str(d / "CX77500_*.bin")):
            b = BK4(p); s, _ = b.entry(0x300AB); q = b.ptr(0x300AB); raws.add(b.d[q:q + s])
        self.assertEqual(len(raws), 1)


class ChainEmulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = e3_chain.run()

    def test_pairs_and_classification(self):
        r = self.r
        self.assertEqual(r["stubbed"], {})
        self.assertTrue(r["classification"].startswith("PERMITIDO"))
        self.assertEqual(r["pairs"][5], (0x2EA0, 0x6028))
        mid = r["p0_output"]
        want = [(mid["0x314"], mid["0x316"]), (mid["0x318"], mid["0x31a"]), (mid["0x31c"], mid["0x31e"]),
                (mid["0x320"], mid["0x322"]), (mid["0x328"], mid["0x32a"])]
        self.assertEqual(r["pairs"][:5], want)

    def test_b_disabled_when_stage_3a_not_one(self):
        r = e3_chain.run(stage3a=0)
        self.assertEqual(r["block_hex"], "00" * 24)

    def test_sixth_pair_follows_table(self):
        e = bytearray(e3_chain.bk4_entry())
        struct.pack_into("<HH", e, 0x36 + 4 * 2, 0x1111, 0x2222)   # índice 2 = flag0*9 + (0xd-0xd)*3 + sel2 (stage[1]=0 y obj8[2]=0)
        r = e3_chain.run(t_entry=bytes(e))
        self.assertEqual(r["pairs"][5], (0x1111, 0x2222))


class MessageFlow(unittest.TestCase):
    def test_request_types(self):
        t6 = [(m, o) for _, m, o in dis(0x438062E8, 0x43806310)]
        self.assertIn(("movs", "r3, #6"), t6); self.assertIn(("strb.w", "r3, [sp]"), t6)
        for fn in (0x4380632C, 0x43806398):               # tipo = 1 + 8 = 9
            body = [(m, o) for _, m, o in dis(fn, fn + 0x6C)]
            self.assertIn(("adds", "r3, #8"), body)
            self.assertIn(("bl", "#0x438061c4"), body)

    def test_reply_emitters(self):
        cases = {0x43B00FE6: (1, 3, 4), 0x43B00FA4: (2, 2, 4), 0x43B00F62: (1, 9, 10), 0x43B00F22: (2, 8, 10)}
        for fn, (role, add, typ) in cases.items():
            body = [(m, o) for _, m, o in dis(fn, fn + 0x28)]
            self.assertIn(("cmp", f"r3, #{role}"), body)
            self.assertIn(("adds", f"r3, #{add}"), body)
            self.assertEqual(role + add, typ)

    def test_queue_handles(self):
        self.assertEqual((u32(0x438064A8), u32(0x438064AC)), (0x8003030F, 0x0003030F))
        self.assertEqual((u32(0x4380626C), u32(0x43806E64)), (0x3030F, 0x3030F))
        # los literales 0x3030f / 0x8003030f solo aparecen en este módulo (sin emisores externos con literal)
        hits = [B + i for i in range(0, len(BLOB) - 3, 4) if u32(B + i) in (0x3030F, 0x8003030F)]
        self.assertTrue(all(0x43805900 <= h < 0x43806F00 for h in hits), [hex(h) for h in hits])

    def test_request_methods_have_no_direct_callers(self):
        import xr
        self.assertEqual(xr.callers(0x43B00ED8), [0x437907A6])      # único llamador directo: HS_Main
        self.assertEqual(xr.func_start(0x437907A6), 0x4378FEF4)
        self.assertEqual(sorted(xr.callers(0x4380632C) + xr.callers(0x43806398)), [0x43B00F04, 0x43B00F1C])


class SyncContext(unittest.TestCase):
    def _strings(self, lo, hi):
        out = set()
        for a, m, o in dis(lo, hi):
            mm = re.match(r"(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$", o)
            if m.startswith("ldr") and mm:
                la = ((a + 4) & ~3) + int(mm.group(2), 0)
                v = u32(la)
                for x in dis(a, a + 14):
                    if x[1] == "add" and x[2] == mm.group(1) + ", pc":
                        t = (v + x[0] + 4) & 0xFFFFFFFF
                        if B <= t < B + len(BLOB) - 8:
                            out.add(BLOB[t - B:BLOB.find(b"\0", t - B)])
                        break
        return out

    def test_request_9_sent_from_hs_main_and_publish_in_vd_pre(self):
        hs = self._strings(0x4378FEF4, 0x43790900)
        self.assertTrue(any(s.startswith(b"[CAMERA_MAIN_SYNC]: HS_Main") for s in hs))
        vd = self._strings(0x43792A0C, 0x43792E00)
        self.assertTrue(any(b"VD_Pre" in s for s in vd))
        import xr
        self.assertEqual(xr.callers(0x43B00DD4), [0x43792F62])
        self.assertEqual(xr.func_start(0x43792F62), 0x43792A0C)


class Compatibility(unittest.TestCase):
    def test_s60_payload_probe_still_valid(self):
        p = trace_payload.probe()
        self.assertEqual(p["case4"]["type"], 4)
        self.assertEqual(p["case10"]["type"], 10)
        self.assertEqual(p["input_kind"], "sintético")


if __name__ == "__main__":
    unittest.main()
