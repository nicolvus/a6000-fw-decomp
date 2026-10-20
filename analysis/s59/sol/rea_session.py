"""Ejecuta el daemon existente desviando exclusivamente sus salidas a S59/sol."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "analysis/rea-independent/bin/session_daemon.py"
sys.path.insert(0, str(SOURCE.parent))
code = SOURCE.read_text().replace(
    'os.path.join(os.path.dirname(sock_path), "../out/exp2-session-log.jsonl")',
    'os.path.join(os.path.dirname(sock_path), "rea-session.jsonl")',
)
# Fuente fija del repositorio: se conserva el daemon y solo se cambia su log.
exec(compile(code, str(SOURCE), "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})  # noqa: S102
