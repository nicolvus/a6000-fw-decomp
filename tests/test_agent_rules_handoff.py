"""El orden del repo lo fija `ORDEN.md` y su copia de lectura vive en `a6000-handoff-context`.

`estado/ORDEN.md` y `estado/ORDER.md` replican este repositorio y se traen con
`scripts/agent/sync_rules.sh` (`ORDEN.md` §12). Si una superficie de instrucciones deja de nombrar
la regla, o el script pierde el manejo de la copia, este test falla.
"""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agent" / "sync_rules.sh"
AGENT_SURFACES = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "docs" / "agent" / "README.md"]
ORDER_DOCS = [ROOT / "ORDEN.md", ROOT / "ORDER.md"]


class HandoffRules(unittest.TestCase):
    def test_agent_surfaces_point_to_the_reading_copy(self):
        for path in AGENT_SURFACES:
            with self.subTest(surface=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn("a6000-handoff-context", text)
                self.assertIn("sync_rules.sh", text)
                self.assertIn("§12", text)

    def test_order_docs_define_and_fetch_the_copy(self):
        for path in ORDER_DOCS:
            with self.subTest(document=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn("a6000-handoff-context", text)
                self.assertIn("sync_rules.sh", text)
                self.assertIn("## 12.", text)

    def test_script_maps_the_reading_copies(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("estado/ORDEN.md", text)
        self.assertIn("Read-only copy", text)  # nota de cabecera que no cuenta como diferencia

    def test_script_is_present_and_executable(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertTrue(SCRIPT.stat().st_mode & 0o111)

    def test_script_syntax(self):
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("sin bash")
        subprocess.run([bash, "-n", str(SCRIPT)], check=True)

    def test_cache_is_git_ignored(self):
        self.assertIn(".handoff-rules/", (ROOT / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
