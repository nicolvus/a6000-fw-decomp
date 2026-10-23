"""S329 - tests del carril B: tablas por modo del A7S y ausencia de tabla de tiempos."""
import json
import struct
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s329_mode_timing_tables/mode_timing.json"
VERIFY = ROOT / "analysis/s329_mode_timing_tables/verify_mode_timing.py"
BASE = 0x43541000
A7S = ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
              "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6000 = ROOT / ("firmware/extracted/fw321/firmware.tar_unpacked/"
                "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")


class ModeTiming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())
        cls.a7 = A7S.read_bytes()
        cls.a6 = A6000.read_bytes()

    def u32(self, blob, addr):
        return struct.unpack_from("<I", blob, addr - BASE)[0]

    def u16(self, blob, addr):
        return struct.unpack_from("<H", blob, addr - BASE)[0]

    def test_bases_from_pic(self):
        bases = self.d["bases_from_pic"]
        self.assertEqual(bases["T1"]["base"], "0x43bbeb70")
        self.assertEqual(bases["T2"]["base"], "0x43bbf2e8")
        self.assertEqual(bases["T3"]["base"], "0x43bbef30")
        self.assertEqual(bases["B"]["base"], "0x43c9d09b")
        for info in bases.values():
            # un solo literal en todo el blob: un solo consumidor
            self.assertEqual(len(info["literal_hits"]), 1)

    def test_s317_bases_are_four_bytes_high(self):
        coh = self.d["base_coherence"]
        for name, s317 in (("T2", "0x43bbf2ec"), ("T3", "0x43bbef34")):
            self.assertEqual(coh[name]["s317_base"], s317)
            self.assertEqual(int(s317, 16) - int(coh[name]["code_base"], 16), 4)
            self.assertTrue(coh[name]["code_index_within_B"])
        self.assertEqual(coh["spacing"]["T3_to_T2_rows"], 34)

    def test_bias_calibration(self):
        cal = self.d["bias_calibration"]
        self.assertEqual(cal["verdict"], "PC=(add+4) con bit0 a 0")
        self.assertGreater(cal["only_bit0_clear"], 1000)
        self.assertLess(cal["only_align4"], 20)

    def test_descriptor_b_has_two_rows(self):
        b = self.d["descriptor_b"]
        self.assertEqual(b["rows_available"], 2)
        self.assertTrue(b["row0_is_identity"])
        self.assertEqual(b["row1"], [0, 7, 6, 1, 2, 9, 8, 3, 4, 11, 10, 5])
        # la tercera "fila" ya es texto
        self.assertTrue(b["bytes_after_two_rows_ascii"].startswith("GCS2RxLink"))
        base = int(b["base"], 16)
        self.assertEqual(list(self.a7[base - BASE:base - BASE + 12]), list(range(12)))

    def test_t_rows_index_and_mask(self):
        stats = {k: v["field_stats"] for k, v in self.d["tables"].items()}
        self.assertEqual(stats["T1"]["index_values"], ["0x0"])
        self.assertEqual(stats["T2"]["index_values"], ["0x0"])
        self.assertEqual(stats["T3"]["index_values"], ["0x0", "0x1"])
        for table in stats.values():
            self.assertTrue(table["index_within_B_rows"])
            self.assertTrue(table["masks_within_12_bits"])

    def test_consumer_reads_only_index_and_mask(self):
        cons = self.d["consumer"]
        self.assertEqual(cons["address"], "0x436f618c")
        reads = {fr["table"]: fr["insn"] for fr in cons["field_reads"]}
        self.assertEqual(len(cons["field_reads"]), 6)
        for insn in reads.values():
            self.assertIn(insn.split()[0], ("ldr", "ldrh"))
        self.assertEqual(cons["bytes_never_read_per_row"], 0x1C - 6)

    def test_matrix_silent_diffs(self):
        diffs = {f"{p['a']}/{p['b']}": p["count"]
                 for p in self.d["matrix_pair_diffs"]}
        self.assertEqual(diffs["0x4e/0x4c"], 14)
        self.assertEqual(diffs["0x4f/0x4d"], 11)
        self.assertEqual(diffs["0x4c/0x4d"], 0)
        self.assertEqual(diffs["0x4e/0x51"], 4)
        self.assertEqual(diffs["0x4f/0x50"], 4)

    def test_no_exclusive_silent_register_value(self):
        mv = self.d["mode_vectors"]
        self.assertEqual(mv["exclusive_silent_values"], [])
        self.assertEqual(mv["unique_column_vectors"], 16)
        self.assertTrue(mv["silent_columns_unique"]["12"])
        self.assertTrue(mv["silent_columns_unique"]["13"])

    def test_t2_pairs_not_identical(self):
        # S326 afirmo 0x4e==0x51 y 0x4f==0x50 con la base +4; no se sostiene
        pairs = {f"{p['a']}/{p['b']}": p["identical"]
                 for p in self.d["t_row_pairs"]["T2"]}
        self.assertFalse(pairs["0x4e/0x51"])
        self.assertFalse(pairs["0x4f/0x50"])
        self.assertTrue(pairs["0x4c/0x4d"])
        pairs_t1 = {f"{p['a']}/{p['b']}": p["identical"]
                    for p in self.d["t_row_pairs"]["T1"]}
        self.assertTrue(pairs_t1["0x4e/0x4c"])

    def test_no_timing_table_in_sweep(self):
        sw = self.d["timing_table_sweep"]
        self.assertEqual(sw["tablas_T"]["strict_time"], [])
        for hit in sw["lista_y_matriz"]["strict_time"]:
            # descartado: valores 1..78, no son tiempos
            self.assertLessEqual(hit["max"], 78)
        self.assertFalse(self.d["verdicts"]["timing_table_exists"])

    def test_setter_ranges(self):
        self.assertIn("#0x51", self.d["setters"]["a7s"]["insn"])
        self.assertIn("#0x47", self.d["setters"]["a6000"]["insn"])
        self.assertEqual(self.a6[0x436D6B62 - BASE:0x436D6B62 - BASE + 2].hex(), "472a")

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("0 fallos", res.stdout)

    def test_limits_recorded(self):
        text = " ".join(self.d["limits"])
        self.assertIn("runtime", text)
        self.assertIn("S51", text)


if __name__ == "__main__":
    unittest.main()
