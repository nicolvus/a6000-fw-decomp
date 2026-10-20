"""Ejecuta knowledge-maintenance con DB y exportaciones aisladas en S60."""
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts/knowledge"))
from export_corrections import export_corrections, export_open_questions


def main():
    with tempfile.TemporaryDirectory(prefix="s60-sol-knowledge-") as directory:
        db = Path(directory) / "knowledge.sqlite"
        source = sqlite3.connect(
            f"file:{ROOT / '.knowledge-cache/knowledge.sqlite'}?mode=ro", uri=True,
        )
        target = sqlite3.connect(db)
        try:
            source.backup(target)
        finally:
            source.close()
            target.close()
        totals = []
        for step in ("index_docs.py", "build_graph.py", "export", "index_docs.py", "build_graph.py"):
            if step == "export":
                connection = sqlite3.connect(db)
                try:
                    a = export_corrections(connection, OUT / "knowledge-corrections.txt")
                    b = export_open_questions(connection, OUT / "knowledge-open-questions.txt")
                    print("exportaciones aisladas:", a, b, flush=True)
                finally:
                    connection.close()
                continue
            result = subprocess.run(
                [str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/knowledge" / step),
                 "--db", str(db)], cwd=ROOT, capture_output=True, text=True, check=True,
            )
            print(step, result.stdout.strip(), flush=True)
            if step == "build_graph.py":
                connection = sqlite3.connect(db)
                try:
                    totals.append(connection.execute("SELECT count(*) FROM relations").fetchone()[0])
                finally:
                    connection.close()
        if len(totals) != 2 or totals[0] != totals[1]:
            raise RuntimeError(f"Grafo inestable: {totals}")
        print("Estabilidad verificada:", totals, flush=True)


if __name__ == "__main__":
    main()
