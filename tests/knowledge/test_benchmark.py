"""Regresión del benchmark: estructura del reporte, no valores absolutos (dependen
de la máquina). Usa un corpus de prueba pequeño, no el repositorio real completo."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"
BENCH_SCRIPT = ROOT / "scripts" / "knowledge" / "benchmark.py"


class BenchmarkTest(unittest.TestCase):
    def test_report_has_one_row_per_method_per_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "proj"
            (proj / "docs" / "capture").mkdir(parents=True)
            (proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
            (proj / "docs" / "capture" / "topic.md").write_text(
                "# Resultado sobre 0xDEADBEEF\n\n"
                "El registro 0xDEADBEEF controla el obturador EFCS.\n"
            )
            db = Path(tmp) / "knowledge.sqlite"
            subprocess.run(
                [sys.executable, str(INDEX_SCRIPT), "--db", str(db)],
                cwd=proj, check=True, capture_output=True, text=True,
            )
            out_report = proj / "report.md"
            result = subprocess.run(
                [sys.executable, str(BENCH_SCRIPT), "--out", str(out_report)],
                cwd=proj, check=True, capture_output=True, text=True,
            )
            self.assertIn("Aciertos:", result.stdout)
            data = json.loads(out_report.with_suffix(".json").read_text())
            # 7 consultas de referencia * 3 métodos cada una = 21 filas
            self.assertEqual(len(data), 21)
            for row in data:
                self.assertIn("latency_s", row)
                self.assertIn("approx_tokens_estimate", row)
                self.assertIn("hit", row)


if __name__ == "__main__":
    unittest.main()
