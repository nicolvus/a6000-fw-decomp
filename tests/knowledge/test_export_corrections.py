"""Regresión: export_corrections.py refleja exactamente las relaciones del grafo."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"
GRAPH_SCRIPT = ROOT / "scripts" / "knowledge" / "build_graph.py"
EXPORT_SCRIPT = ROOT / "scripts" / "knowledge" / "export_corrections.py"


class ExportCorrectionsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = Path(self._tmp.name) / "knowledge.sqlite"

    def tearDown(self):
        self._tmp.cleanup()

    def run_script(self, script):
        return subprocess.run(
            [sys.executable, str(script), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )

    def test_export_matches_graph_relation_count(self):
        (self.proj / "docs" / "capture" / "old.md").write_text(
            "# Resultado original\n\nNO_VERIFICADO: falta confirmar el banco B.\n"
        )
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Resultado nuevo\n\nCORRECCIÓN: corrige [lo anterior](old.md).\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        result = self.run_script(EXPORT_SCRIPT)

        self.assertIn("CORRECTIONS.md: 1 filas", result.stdout)
        self.assertIn("OPEN-QUESTIONS.md: 1 filas", result.stdout)

        corrections = (self.proj / "docs" / "CORRECTIONS.md").read_text()
        self.assertIn("old.md", corrections)
        self.assertIn("new.md", corrections)
        self.assertIn("CORRECTS", corrections)

        open_questions = (self.proj / "docs" / "OPEN-QUESTIONS.md").read_text()
        self.assertIn("old.md", open_questions)

    def test_open_questions_ignores_sections_that_only_mention_the_word(self):
        # Antes export_open_questions buscaba por texto libre NO_VERIFICADO/CONFLICTO_PENDIENTE
        # en cualquier sección: una sección que solo EXPLICA el vocabulario (sin ser realmente
        # una relación abierta del grafo) se contaba como pregunta abierta. Ahora debe venir
        # del grafo: solo relaciones reales con ese status.
        (self.proj / "docs" / "capture" / "vocab.md").write_text(
            "# Vocabulario de status\n\n"
            "Los valores posibles son VERIFICADO, PARCIAL, NO_VERIFICADO y CONFLICTO_PENDIENTE.\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        result = self.run_script(EXPORT_SCRIPT)

        self.assertIn("OPEN-QUESTIONS.md: 0 filas", result.stdout)
        open_questions = (self.proj / "docs" / "OPEN-QUESTIONS.md").read_text()
        self.assertNotIn("vocab.md", open_questions)

    def test_rebuilding_graph_after_export_does_not_self_contaminate(self):
        """docs/CORRECTIONS.md cita 'CORRECTS' y enlaza a muchos documentos por diseño;
        reindexarlo y reconstruir el grafo NO debe generar relaciones nuevas a partir
        de su propio contenido (sería circular: el export contaminando su propia fuente)."""
        (self.proj / "docs" / "capture" / "old.md").write_text("# Resultado original\n\ncontenido\n")
        (self.proj / "docs" / "capture" / "new.md").write_text(
            "# Resultado nuevo\n\nCORRECCIÓN: corrige [lo anterior](old.md).\n"
        )
        self.run_script(INDEX_SCRIPT)
        self.run_script(GRAPH_SCRIPT)
        self.run_script(EXPORT_SCRIPT)

        self.run_script(INDEX_SCRIPT)  # ahora indexa también docs/CORRECTIONS.md generado
        result = self.run_script(GRAPH_SCRIPT)
        self.assertIn("Correcciones: 1 relaciones", result.stdout)


if __name__ == "__main__":
    unittest.main()
