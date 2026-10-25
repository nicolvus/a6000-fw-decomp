"""Regresión de cmd_trace (Fase 12.5): consulta multietapa sobre relaciones reales del
grafo, encadenando varios saltos, sin ciclos y sin inventar relaciones inexistentes."""

import contextlib
import importlib.util
import io
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH_SCRIPT = ROOT / "scripts" / "knowledge" / "search.py"

sys.path.insert(0, str(ROOT / "scripts" / "knowledge"))
spec = importlib.util.spec_from_file_location("search", SEARCH_SCRIPT)
assert spec and spec.loader
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class TraceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db = Path(self._tmp.name) / "knowledge.sqlite"
        conn = sqlite3.connect(self.db)
        conn.executescript(search.__dict__.get("SCHEMA", "") or "")
        conn.executescript(
            "CREATE TABLE relations (id TEXT PRIMARY KEY, src_id TEXT, dst_id TEXT, "
            "type TEXT, status TEXT, extraction_method TEXT, owner_source TEXT, "
            "source_path TEXT, line_start INTEGER, line_end INTEGER, evidence TEXT);"
        )
        # A -> B -> C (2 saltos reales); D no está conectado a nada
        conn.executemany(
            "INSERT INTO relations VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [
                ("r1", "A", "B", "CALLS", "PARCIAL", "test", "f.json", "f.json", 1, 1, "A llama a B"),
                ("r2", "B", "C", "CALLS", "PARCIAL", "test", "f.json", "f.json", 2, 2, "B llama a C"),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, start, **kwargs):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            search.cmd_trace(str(self.db), start, kwargs.get("direction", "out"),
                              kwargs.get("max_hops", 3), kwargs.get("rel_type"))
        return buf.getvalue()

    def test_two_hop_chain_is_followed(self):
        output = self._run("A")
        self.assertIn("A --CALLS--> B", output)
        self.assertIn("B --CALLS--> C", output)
        self.assertIn("salto 1", output)
        self.assertIn("salto 2", output)

    def test_max_hops_limits_depth(self):
        output = self._run("A", max_hops=1)
        self.assertIn("A --CALLS--> B", output)
        self.assertNotIn("B --CALLS--> C", output)

    def test_disconnected_node_reports_no_relations_not_an_error(self):
        output = self._run("D")
        self.assertIn("Sin relaciones desde D", output)

    def test_reverse_direction_follows_incoming_edges(self):
        output = self._run("C", direction="in")
        self.assertIn("C --CALLS--> B", output)
        self.assertIn("B --CALLS--> A", output)


if __name__ == "__main__":
    unittest.main()
