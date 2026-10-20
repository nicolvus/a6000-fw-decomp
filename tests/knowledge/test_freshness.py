"""Regresión: search.py freshness detecta archivos editados/añadidos/eliminados desde
el último index_docs.py (antes no existía ninguna comprobación de que el índice
correspondiera a la versión actual de sus archivos)."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"
SEARCH_SCRIPT = ROOT / "scripts" / "knowledge" / "search.py"

sys.path.insert(0, str(ROOT / "scripts" / "knowledge"))
spec = importlib.util.spec_from_file_location("search", SEARCH_SCRIPT)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class FreshnessTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = Path(self._tmp.name) / "knowledge.sqlite"
        self.doc = self.proj / "docs" / "capture" / "topic.md"
        self.doc.write_text("# Tema\n\nContenido original.\n")
        subprocess.run(
            [sys.executable, str(INDEX_SCRIPT), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )
        self._orig_root = search.ROOT

    def tearDown(self):
        search.ROOT = self._orig_root
        self._tmp.cleanup()

    def _run_freshness(self):
        import contextlib
        import io
        import os

        cwd = os.getcwd()
        os.chdir(self.proj)
        search.ROOT = self.proj  # ROOT se fija una sola vez al importar el módulo; se ajusta
        # aquí para que apunte al proyecto de prueba (ver nota equivalente en test_adaptive_search.py)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_freshness(str(self.db))
            return buf.getvalue()
        finally:
            os.chdir(cwd)

    def test_fresh_index_reports_up_to_date(self):
        self.assertIn("al día", self._run_freshness())

    def test_modified_file_is_detected(self):
        self.doc.write_text("# Tema\n\nContenido EDITADO tras indexar.\n")
        output = self._run_freshness()
        self.assertIn("DESACTUALIZADO", output)
        self.assertIn("modificado", output)
        self.assertIn("docs/capture/topic.md", output)

    def test_new_unindexed_file_is_detected(self):
        (self.proj / "docs" / "capture" / "nuevo.md").write_text("# Nuevo\n\ncontenido\n")
        output = self._run_freshness()
        self.assertIn("nuevo sin indexar", output)

    def test_deleted_file_still_in_index_is_detected(self):
        self.doc.unlink()
        output = self._run_freshness()
        self.assertIn("eliminado pero sigue en el índice", output)


if __name__ == "__main__":
    unittest.main()
