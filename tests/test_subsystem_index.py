"""docs/INDEX.md debe listar cada informe de docs/capture/ y estar al día con su generador."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_todos_los_informes_estan_indexados():
    index = (ROOT / "docs" / "INDEX.md").read_text()
    faltan = [p.name for p in (ROOT / "docs" / "capture").glob("*.md") if p.name != "README.md" and f"(capture/{p.name})" not in index]
    assert not faltan, faltan


def test_indice_generado_al_dia():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "knowledge" / "build_subsystem_index.py"), "--check"])
    assert r.returncode == 0, "ejecuta scripts/knowledge/build_subsystem_index.py"
