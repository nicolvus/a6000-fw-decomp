"""Abre el daemon REA canónico y guarda su registro dentro de S60."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "analysis/rea-independent/bin/session_daemon.py"
sys.path.insert(0, str(SOURCE.parent))
code = SOURCE.read_text().replace(
    'os.path.join(os.path.dirname(sock_path), "../out/exp2-session-log.jsonl")',
    'os.path.join(os.path.dirname(sock_path), "rea-session.jsonl")',
)
exec(compile(code, str(SOURCE), "exec"), {"__name__": "__main__", "__file__": str(SOURCE)})  # noqa: S102
