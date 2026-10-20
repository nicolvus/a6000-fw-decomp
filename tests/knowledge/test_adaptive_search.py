"""Regresión del enrutador de recuperación adaptativa (ask): clasificación de consulta,
deduplicación y recorte por presupuesto de caracteres."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_SCRIPT = ROOT / "scripts" / "knowledge" / "index_docs.py"
SEARCH_SCRIPT = ROOT / "scripts" / "knowledge" / "search.py"

sys.path.insert(0, str(ROOT / "scripts" / "knowledge"))  # search.py hace `from _paths import find_root`
spec = importlib.util.spec_from_file_location("search", SEARCH_SCRIPT)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class ClassifyQueryTest(unittest.TestCase):
    def test_hex_address_is_identifier(self):
        self.assertEqual(search.classify_query("0x4383fd6c"), "identifier")

    def test_bare_symbol_is_identifier(self):
        self.assertEqual(search.classify_query("SetImageWrited"), "identifier")

    def test_md_path_is_doc(self):
        self.assertEqual(search.classify_query("docs/capture/s27-effect-postprocess-rewire.md"),
                          "doc")

    def test_multi_word_is_concept(self):
        self.assertEqual(search.classify_query("Darwin base ROM"), "concept")


class AskRouterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = Path(self._tmp.name) / "knowledge.sqlite"
        (self.proj / "docs" / "capture" / "topic.md").write_text(
            "# Resultado sobre 0xDEADBEEF\n\n"
            "El registro 0xDEADBEEF controla el obturador. Concepto EFCS relevante.\n"
        )
        subprocess.run(
            [sys.executable, str(INDEX_SCRIPT), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_ask_respects_budget_and_reports_truncation(self):
        import contextlib
        import io
        import os

        cwd = os.getcwd()
        os.chdir(self.proj)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_ask(str(self.db), "EFCS obturador", budget=50)
            output = buf.getvalue()
        finally:
            os.chdir(cwd)
        self.assertIn("resultado(s) mostrados", output)
        self.assertIn("caracteres de", output)

    def test_single_oversized_block_is_truncated_not_printed_whole(self):
        # Bug de la auditoría: "el presupuesto de ask puede superarse con el primer
        # resultado". _budget_print imprimía el primer bloque COMPLETO aunque él solo ya
        # superase el presupuesto (la condición `shown > 0` lo eximía del recorte).
        blocks = ["X" * 500]
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            search._budget_print(blocks, budget=50)
        body = buf.getvalue().split("\n[")[0]
        self.assertLessEqual(len(body), 80)  # recortado (50 + margen del aviso de truncado)

    def test_budget_print_never_exceeds_budget_across_multiple_blocks(self):
        import contextlib
        import io
        blocks = ["A" * 30, "B" * 30, "C" * 30]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            search._budget_print(blocks, budget=50)
        output = buf.getvalue()
        shown_line = next(line for line in output.splitlines() if "resultado(s) mostrados" in line)
        used = int(shown_line.split("~")[1].split("/")[0])
        self.assertLessEqual(used, 50)


class ExactGlobalLimitTest(unittest.TestCase):
    """rg --max-count limita por ARCHIVO, no en total; cmd_exact debía aplicar el límite
    globalmente sobre el conjunto combinado de líneas de todos los archivos."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        for i in range(3):
            lines = "\n".join(f"EXACTTERM línea {j}" for j in range(5))
            (self.proj / "docs" / "capture" / f"doc{i}.md").write_text(f"# Doc {i}\n\n{lines}\n")
        self._orig_root = search.ROOT

    def tearDown(self):
        search.ROOT = self._orig_root
        self._tmp.cleanup()

    def test_global_limit_caps_total_lines_across_all_files(self):
        import contextlib
        import io
        import os

        cwd = os.getcwd()
        os.chdir(self.proj)
        search.ROOT = self.proj  # ROOT se fija al importar el módulo (una sola vez por
        # proceso); el chdir de este test no lo actualiza retroactivamente, así que se
        # ajusta explícitamente para que apunte al proyecto de prueba, igual que ocurriría
        # si este módulo se cargara de cero dentro de ese directorio.
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_exact("EXACTTERM", limit=4)
            output = buf.getvalue()
        finally:
            os.chdir(cwd)
        match_lines = [line for line in output.splitlines() if "EXACTTERM" in line]
        self.assertEqual(len(match_lines), 4)  # 15 coincidencias totales (3 archivos x 5), tope global=4
        self.assertIn("límite global", output)


class ExactStreamingCapTest(unittest.TestCase):
    """Fase 12.2.B: cmd_exact debe leer en streaming y cortar por RG_MAX_SCAN/timeout,
    no materializar toda la salida de rg antes de aplicar el límite."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")
        lines = "\n".join(f"MANYTERM línea {j}" for j in range(search.RG_MAX_SCAN + 50))
        (self.proj / "docs" / "capture" / "big.md").write_text(f"# Big\n\n{lines}\n")
        self._orig_root = search.ROOT

    def tearDown(self):
        search.ROOT = self._orig_root
        self._tmp.cleanup()

    def test_scan_cap_stops_before_reading_everything(self):
        import contextlib
        import io
        import os

        cwd = os.getcwd()
        os.chdir(self.proj)
        search.ROOT = self.proj
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_exact("MANYTERM", limit=5)
            output = buf.getvalue()
        finally:
            os.chdir(cwd)
        match_lines = [line for line in output.splitlines() if "MANYTERM" in line]
        self.assertEqual(len(match_lines), 5)
        self.assertIn("+", output)  # total aproximado: se cortó antes de contar todo


class SectionSubtreeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = Path(self._tmp.name) / "knowledge.sqlite"
        (self.proj / "docs" / "capture" / "nested.md").write_text(
            "# Padre\n\nContenido propio del padre.\n\n"
            "## Hijo\n\nContenido del hijo.\n\n"
            "# Siguiente padre\n\nOtro contenido.\n"
        )
        subprocess.run(
            [sys.executable, str(INDEX_SCRIPT), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )
        self._orig_root = search.ROOT

    def tearDown(self):
        search.ROOT = self._orig_root
        self._tmp.cleanup()

    def test_default_section_excludes_children(self):
        import contextlib
        import io
        import os
        import sqlite3

        with sqlite3.connect(self.db) as c:
            node_id = c.execute(
                "SELECT id FROM nodes WHERE heading = 'Padre'"
            ).fetchone()[0]
        cwd = os.getcwd()
        os.chdir(self.proj)
        search.ROOT = self.proj
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_section(str(self.db), node_id, subtree=False)
            output = buf.getvalue()
        finally:
            os.chdir(cwd)
        self.assertIn("Contenido propio del padre", output)
        self.assertNotIn("Contenido del hijo", output)

    def test_subtree_includes_children_but_not_next_sibling(self):
        import contextlib
        import io
        import os
        import sqlite3

        with sqlite3.connect(self.db) as c:
            node_id = c.execute(
                "SELECT id FROM nodes WHERE heading = 'Padre'"
            ).fetchone()[0]
        cwd = os.getcwd()
        os.chdir(self.proj)
        search.ROOT = self.proj
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_section(str(self.db), node_id, subtree=True)
            output = buf.getvalue()
        finally:
            os.chdir(cwd)
        self.assertIn("Contenido propio del padre", output)
        self.assertIn("Contenido del hijo", output)
        self.assertNotIn("Otro contenido", output)


class TextPaginationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.proj = Path(self._tmp.name) / "proj"
        (self.proj / "docs" / "capture").mkdir(parents=True)
        (self.proj / "CLAUDE.md").write_text("")  # marcador de raíz de proyecto aislado
        self.db = Path(self._tmp.name) / "knowledge.sqlite"
        for i in range(3):
            (self.proj / "docs" / "capture" / f"doc{i}.md").write_text(
                f"# Tema {i}\n\nContiene la palabra PAGINATIONTERM en el documento {i}.\n"
            )
        subprocess.run(
            [sys.executable, str(INDEX_SCRIPT), "--db", str(self.db)],
            cwd=self.proj, check=True, capture_output=True, text=True,
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_offset_returns_different_page(self):
        import contextlib
        import io

        def run(offset):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                search.cmd_text("PAGINATIONTERM", limit=1, db=str(self.db), offset=offset)
            return buf.getvalue()

        page0, page1 = run(0), run(1)
        self.assertNotEqual(page0.splitlines()[0], page1.splitlines()[0])


if __name__ == "__main__":
    unittest.main()
