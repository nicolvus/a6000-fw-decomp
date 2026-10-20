"""Regresión: checkpoint.py crea/lista/muestra checkpoints estructurados reales."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "knowledge" / "checkpoint.py"


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        self.proj.mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )

    def test_create_writes_all_required_fields(self):
        self.run_cli(
            "create", "--goal", "Probar checkpoints",
            "--done", "paso 1", "--done", "paso 2",
            "--file", "scripts/knowledge/checkpoint.py",
            "--finding", "hallazgo X", "--evidence", "doc.md:10",
            "--test", "pytest -> OK", "--blocker", "ninguno",
            "--next-action", "siguiente paso", "--permissions", "ninguno pendiente",
        )
        checkpoints = list((self.proj / "knowledge" / "checkpoints").glob("*.json"))
        self.assertEqual(len(checkpoints), 1)
        data = json.loads(checkpoints[0].read_text())
        self.assertEqual(data["goal"], "Probar checkpoints")
        self.assertEqual(data["done"], ["paso 1", "paso 2"])
        self.assertEqual(data["permissions_state"], "ninguno pendiente")
        self.assertIn("schema_version", data)

    def test_list_and_latest_reflect_created_checkpoint(self):
        self.run_cli("create", "--goal", "Primero")
        self.run_cli("create", "--goal", "Segundo")
        listed = self.run_cli("list").stdout
        self.assertIn("Primero", listed)
        self.assertIn("Segundo", listed)
        latest = self.run_cli("latest").stdout
        self.assertIn("Segundo", latest)
        self.assertNotIn("Primero", latest)

    def test_show_by_partial_id(self):
        self.run_cli("create", "--goal", "Con id")
        checkpoint_path = next((self.proj / "knowledge" / "checkpoints").glob("*.json"))
        short_id = checkpoint_path.stem.split("-")[-1]
        result = self.run_cli("show", short_id)
        self.assertIn("Con id", result.stdout)


if __name__ == "__main__":
    unittest.main()
