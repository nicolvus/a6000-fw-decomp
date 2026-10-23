"""S347 - tests del carril B: campo 0x000d de la tabla ODL e ids A6000 vs A7S."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s347_odl_field/odl_field.json"
VERIFY = ROOT / "analysis/s347_odl_field/verify_odl_field.py"


class OdlField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_segundo_campo_constante(self):
        for k, m in self.d["models"].items():
            self.assertEqual(m["table"]["second_fields"], [0x000D], k)
            self.assertTrue(m["table"]["second_constant"], k)
        self.assertFalse(self.d["verdicts"]["second_field_is_per_id_data"])

    def test_13_en_camino_de_carga_y_en_alloc(self):
        fm = self.d["field_meaning"]
        self.assertEqual(set(fm["same_value_in_load_path"].values()), {0x0D})
        self.assertEqual(set(fm["same_value_in_group_alloc"].values()), {0x0D})
        self.assertEqual(set(fm["header_capacity"].values()), {0x18})
        self.assertFalse(self.d["verdicts"]["13_equals_message_header_size"])

    def test_id_en_el_mensaje(self):
        for k, m in self.d["models"].items():
            store = m["load_path"]["id_store"]["insn"]
            self.assertIn("#0x12", store, k)
            self.assertTrue(store.startswith("strh"), k)
        self.assertTrue(self.d["verdicts"]["id_is_u16_at_message_offset_0x12"])
        self.assertTrue(self.d["field_meaning"]["message_prologue_identical"])

    def test_relacion_entre_modelos(self):
        cm = self.d["cross_model"]
        self.assertEqual(cm["entries"], {"a7s_fw320": 69, "a6000_fw321": 47,
                                         "a6300_fw201": 69})
        self.assertTrue(cm["a6000_equals_a7s_filtered_le_0x4e"])
        self.assertTrue(cm["a6300_equals_a7s"])
        self.assertEqual(cm["a6000_missing"], list(range(79, 101)))
        self.assertEqual(cm["shared_prefix_entries"], 41)
        self.assertEqual(set(cm["loop_iterations"].values()), {69, 47})

    def test_bucles_cerrados_por_modelo(self):
        m = self.d["models"]
        self.assertEqual(m["a7s_fw320"]["consumers"]["A"]["closed_loop"]["imm"], 0x45)
        self.assertEqual(m["a6000_fw321"]["consumers"]["A"]["closed_loop"]["imm"], 0x2F)
        self.assertEqual(m["a6000_fw321"]["consumers"]["B"]["closed_loop"]["imm"], 0xBC)
        self.assertEqual(m["a6300_fw201"]["consumers"]["B"]["closed_loop"]["imm"], 0x114)

    def test_lensbin_no_es_la_fuente(self):
        lb = self.d["lens_aberration_file"]
        self.assertTrue(lb["identical_across_models"])
        self.assertEqual(set(lb["sizes"].values()), {161766})
        self.assertEqual(lb["max_consecutive_pairs_with_second_0x000d"], 1)
        self.assertFalse(lb["contains_a7s_id_list"])
        self.assertFalse(self.d["verdicts"]["ids_index_the_lensbin_file"])

    def test_persistencia_config(self):
        for k, m in self.d["models"].items():
            cp = m["config_persistence"]
            self.assertIn("#0x680", cp["write"]["insn"], k)
            self.assertIn("#0x680", cp["read"]["insn"], k)
            self.assertEqual(cp["config_id_write"]["insn"], "movw r0, #0x402", k)
            self.assertEqual(cp["config_id_read"]["insn"], "movw r0, #0x402", k)

    def test_negativos(self):
        n = self.d["negatives"]
        self.assertEqual(set(n["absolute_literal_refs_to_table"].values()), {0})
        for k, sites in n["pic_bases_to_table"].items():
            self.assertEqual(len(sites), 2, k)
        # 20 codigos de drive mode coinciden numericamente con ids: no confundirlos
        self.assertEqual(len(n["mode_codes_intersect_ids_a7s"]), 20)

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("comprobaciones OK", res.stdout)


if __name__ == "__main__":
    unittest.main()
