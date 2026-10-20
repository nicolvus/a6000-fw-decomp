"""Las skills de agente deben existir iguales en .claude/skills y .agents/skills.

Claude Code lee `.claude/skills`; Codex/DSH leen `.agents/skills`. En Linux las
segundas eran symlinks, lo que rompe en Windows y al clonar con core.symlinks=false.
Este test impone copias reales y evita que las dos ramas se separen.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".agents" / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def skills(root: Path) -> dict[str, Path]:
    found = {}
    for path in sorted(root.glob("*/SKILL.md")):
        found[path.parent.name] = path
    return found


class AgentSkillsSync(unittest.TestCase):
    def test_both_roots_have_the_same_skill_set(self):
        self.assertEqual(sorted(skills(CLAUDE)), sorted(skills(AGENTS)))

    def test_copies_are_byte_identical(self):
        for name, path in skills(CLAUDE).items():
            with self.subTest(skill=name):
                self.assertIn(name, skills(AGENTS))
                self.assertEqual(path.read_bytes(), skills(AGENTS)[name].read_bytes())

    def test_frontmatter_is_valid(self):
        for name, path in sorted(skills(AGENTS).items()):
            with self.subTest(skill=name):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), "falta frontmatter YAML")
                end = text.index("\n---", 4)
                header = text[4:end]
                self.assertIn(f"name: {name}", header)
                self.assertRegex(name, NAME_RE)
                self.assertIn("description:", header)
                self.assertGreater(len(text), len(header) + 200, "cuerpo sospechosamente corto")

    def test_project_root_has_both_rule_files(self):
        for fname in ("AGENTS.md", "CLAUDE.md"):
            with self.subTest(file=fname):
                self.assertTrue((ROOT / fname).is_file())


if __name__ == "__main__":
    unittest.main()
