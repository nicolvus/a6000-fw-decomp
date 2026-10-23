"""S348 - tests del carril B: el callback por entrada del ODL es un memcpy."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "analysis/s348_odl_callback/odl_callback.json"
VERIFY = ROOT / "analysis/s348_odl_callback/verify_odl_callback.py"


class OdlCallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads(JSON.read_text())

    def test_callback_es_adaptador_memcpy(self):
        for k, m in self.d["models"].items():
            self.assertEqual(m["shim"]["bytes"], "10b50c46184611462246", k)
            self.assertEqual(m["shim"]["semantics"], "memcpy(dst=arg4, src=arg3, len=arg2)")
            self.assertEqual(int(m["callback_pointer"], 16) & 1, 1, k)
        self.assertTrue(self.d["verdicts"]["callback_is_memcpy_adapter"])
        self.assertFalse(self.d["verdicts"]["callback_is_data_specific"])

    def test_veneer_y_arm(self):
        for k, m in self.d["models"].items():
            self.assertEqual(m["veneer"]["bytes"][:8], "7847c046", k)
            self.assertTrue(m["veneer"]["arm_target"].startswith("0x43"), k)
            self.assertEqual(m["veneer"]["arm_target"], m["memcpy"]["address"], k)

    def test_memcpy_por_huella(self):
        fps = {tuple(m["memcpy"]["fingerprint"]) for m in self.d["models"].values()}
        self.assertEqual(len(fps), 1)
        self.assertEqual(next(iter(fps)),
                         ("0xe92d4001", "0xe2522004", "0xba000020", "0xe210c003"))
        self.assertTrue(self.d["cross_model"]["memcpy_fingerprint_identical"])

    def test_un_solo_usuario_por_modelo(self):
        users = self.d["cross_model"]["shim_users"]
        for k, u in users.items():
            self.assertEqual(len(u), 1, k)
        self.assertEqual(users["a7s_fw320"], ["0x43705702"])
        self.assertEqual(users["a6000_fw321"], ["0x436eb2e2"])
        self.assertEqual(users["a6300_fw201"], ["0x43734bee"])
        self.assertTrue(self.d["cross_model"]["every_shim_has_one_user"])
        self.assertFalse(self.d["verdicts"]["callback_shared_with_other_services"])

    def test_tamano_por_entrada(self):
        for k, m in self.d["models"].items():
            self.assertEqual(m["spec_word"]["high_half"], 0x0D, k)
        self.assertEqual(self.d["verdicts"]["copy_length_available_per_entry"], 13)
        self.assertTrue(self.d["verdicts"]["direction"].startswith("INFERENCIA"))

    def test_verify_script_passes(self):
        res = subprocess.run([sys.executable, str(VERIFY)], capture_output=True,
                             text=True, check=False)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("comprobaciones OK", res.stdout)


if __name__ == "__main__":
    unittest.main()
