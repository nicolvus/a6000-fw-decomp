"""Regresión: indexación incremental y búsqueda FTS5 sobre un corpus Markdown de prueba."""

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"


class IndexDocsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmp.name)
        self.docs_dir = self.tmp_path / "proj"
        (self.docs_dir / "docs" / "capture").mkdir(parents=True)
        (self.docs_dir / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        (self.docs_dir / "docs" / "capture" / "sample.md").write_text(
            "# Título A\n\nContiene la dirección 0xDEADBEEF.\n\n"
            "## Sección B\n\nTexto sobre EFCS y SilentShutter.\n"
        )
        self.db = self.tmp_path / "knowledge.sqlite"

    def tearDown(self):
        self._tmp.cleanup()

    def run_index(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(self.db)],
            cwd=self.docs_dir, check=True, capture_output=True, text=True,
        )

    def test_index_and_search_roundtrip(self):
        self.run_index()
        conn = sqlite3.connect(self.db)
        sections = conn.execute("SELECT heading, body FROM sections ORDER BY rowid").fetchall()
        self.assertEqual(len(sections), 2)
        self.assertEqual(sections[0][0], "Título A")
        self.assertIn("0xDEADBEEF", sections[0][1])
        self.assertEqual(sections[1][0], "Sección B")

        hits = conn.execute("SELECT path FROM sections WHERE sections MATCH 'EFCS'").fetchall()
        self.assertTrue(hits and hits[0][0] == "docs/capture/sample.md")
        conn.close()

    def test_hierarchy_tree_and_section_retrieval(self):
        self.run_index()
        conn = sqlite3.connect(self.db)
        doc = conn.execute("SELECT subsystem FROM documents").fetchone()
        self.assertEqual(doc[0], "docs/capture")

        nodes = conn.execute(
            "SELECT id, parent_id, level, heading, line_start, line_end FROM nodes ORDER BY seq"
        ).fetchall()
        self.assertEqual(len(nodes), 2)
        root_id, root_parent, root_level, _root_heading, _, _ = nodes[0]
        _child_id, child_parent, child_level, child_heading, c_start, c_end = nodes[1]
        self.assertIsNone(root_parent)
        self.assertEqual(root_level, 1)
        self.assertEqual(child_parent, root_id)
        self.assertEqual(child_level, 2)
        self.assertEqual(child_heading, "Sección B")
        conn.close()

        text = (self.docs_dir / "docs" / "capture" / "sample.md").read_text().splitlines()
        expected = "\n".join(text[c_start - 1:c_end])
        self.assertIn("EFCS y SilentShutter", expected)

    def test_incremental_reindex_skips_unchanged(self):
        r1 = self.run_index()
        self.assertIn("1 archivo", r1.stdout)
        r2 = self.run_index()
        self.assertIn("0 archivo", r2.stdout)

    def test_preamble_before_first_heading_is_preserved(self):
        # Antes split_sections descartaba todo el texto anterior al primer "#": se perdía
        # de la búsqueda cualquier introducción sin encabezado.
        (self.docs_dir / "docs" / "capture" / "preamble.md").write_text(
            "Texto introductorio sin encabezado, menciona PREAMBLEMARKER42.\n\n"
            "# Título\n\nCuerpo normal.\n"
        )
        self.run_index()
        conn = sqlite3.connect(self.db)
        hits = conn.execute(
            "SELECT path FROM sections WHERE sections MATCH 'PREAMBLEMARKER42'"
        ).fetchall()
        conn.close()
        self.assertTrue(hits, "el preámbulo debe quedar indexado y ser buscable")

    def test_preamble_does_not_become_parent_of_first_heading(self):
        (self.docs_dir / "docs" / "capture" / "preamble2.md").write_text(
            "Introducción.\n\n# Título\n\nCuerpo.\n"
        )
        self.run_index()
        conn = sqlite3.connect(self.db)
        nodes = conn.execute(
            "SELECT heading, parent_id FROM nodes WHERE doc_id = 'docs/capture/preamble2.md' "
            "ORDER BY seq"
        ).fetchall()
        conn.close()
        title_parent = next(parent for heading, parent in nodes if heading == "Título")
        self.assertIsNone(title_parent)

    def test_removed_file_is_pruned(self):
        self.run_index()
        (self.docs_dir / "docs" / "capture" / "sample.md").unlink()
        self.run_index()
        conn = sqlite3.connect(self.db)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM files").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0], 0)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0], 0)
        conn.close()


if __name__ == "__main__":
    unittest.main()
