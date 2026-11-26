"""La regla de reglas vigentes (`a6000-handoff-context`) debe estar en todas las superficies.

Las reglas nuevas sobre el orden del repo se publican en el repo privado
`nicolvus/a6000-handoff-context` y se traen con `scripts/agent/sync_rules.sh`. Si alguien
crea una superficie de instrucciones sin la regla, o rompe el script, este test falla.
"""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agent" / "sync_rules.sh"
SURFACES = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "docs" / "agent" / "README.md"]


class HandoffRules(unittest.TestCase):
    def test_every_surface_points_to_the_handoff_repo(self):
        for path in SURFACES:
            with self.subTest(surface=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn("a6000-handoff-context", text)
                self.assertIn("sync_rules.sh", text)

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
