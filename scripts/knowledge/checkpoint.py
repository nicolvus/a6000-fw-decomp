#!/usr/bin/env python3
"""Checkpoints de sesión estructurados (memoria episódica), compartidos por
Claude Code y Codex: un archivo JSON por sesión en knowledge/checkpoints/,
nunca editado a mano directamente por el usuario (se crea con flags de CLI).

Uso:
  python3 scripts/knowledge/checkpoint.py create --goal "..." \\
      --done "..." --file path/a.py --file path/b.py \\
      --finding "..." --evidence "ruta:línea" --correction "..." \\
      --test "pytest tests/knowledge -q -> 19 passed" \\
      --blocker "..." --next "..." --permissions "ninguno pendiente"
  python3 scripts/knowledge/checkpoint.py list
  python3 scripts/knowledge/checkpoint.py latest
  python3 scripts/knowledge/checkpoint.py show <id>
"""

import argparse
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from _paths import find_root

ROOT = find_root()
CHECKPOINTS_DIR = ROOT / "knowledge" / "checkpoints"
SCHEMA_VERSION = 1

REQUIRED_FIELDS = [
    "goal", "done", "files", "findings", "evidence", "corrections",
    "tests", "blockers", "next_actions", "permissions_state",
]


def create(args: argparse.Namespace) -> Path:
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H-%M-%S-%fZ")  # microsegundos: garantiza
    # orden de creación estable aunque dos checkpoints se creen en el mismo segundo
    checkpoint = {
        "schema_version": SCHEMA_VERSION,
        "id": f"{timestamp}-{uuid.uuid4().hex[:8]}",
        "created_at": timestamp,
        "goal": args.goal,
        "done": args.done or [],
        "files": args.file or [],
        "findings": args.finding or [],
        "evidence": args.evidence or [],
        "corrections": args.correction or [],
        "tests": args.test or [],
        "blockers": args.blocker or [],
        "next_actions": args.next_action or [],
        "permissions_state": args.permissions or "sin especificar",
    }
    out_path = CHECKPOINTS_DIR / f"{checkpoint['id']}.json"
    out_path.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def list_checkpoints() -> list[Path]:
    if not CHECKPOINTS_DIR.exists():
        return []
    return sorted(CHECKPOINTS_DIR.glob("*.json"))


def cmd_list() -> None:
    paths = list_checkpoints()
    if not paths:
        print("Sin checkpoints registrados.")
        return
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"{data['id']}  goal: {data['goal']}")


def cmd_show(path: Path) -> None:
    print(path.read_text(encoding="utf-8"))


def cmd_latest() -> None:
    paths = list_checkpoints()
    if not paths:
        print("Sin checkpoints registrados.")
        return
    cmd_show(paths[-1])


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    p_create = sub.add_parser("create", help="registra un checkpoint nuevo")
    p_create.add_argument("--goal", required=True)
    p_create.add_argument("--done", action="append", default=[])
    p_create.add_argument("--file", action="append", default=[])
    p_create.add_argument("--finding", action="append", default=[])
    p_create.add_argument("--evidence", action="append", default=[])
    p_create.add_argument("--correction", action="append", default=[])
    p_create.add_argument("--test", action="append", default=[])
    p_create.add_argument("--blocker", action="append", default=[])
    p_create.add_argument("--next-action", action="append", default=[])
    p_create.add_argument("--permissions", default=None)

    sub.add_parser("list", help="lista los checkpoints registrados")
    sub.add_parser("latest", help="muestra el checkpoint más reciente")

    p_show = sub.add_parser("show", help="muestra un checkpoint por id")
    p_show.add_argument("checkpoint_id")

    args = ap.parse_args()
    if args.mode == "create":
        out_path = create(args)
        print(f"Checkpoint creado: {out_path}")
    elif args.mode == "list":
        cmd_list()
    elif args.mode == "latest":
        cmd_latest()
    elif args.mode == "show":
        matches = [p for p in list_checkpoints() if args.checkpoint_id in p.stem]
        if not matches:
            raise SystemExit(f"Checkpoint no encontrado: {args.checkpoint_id}")
        cmd_show(matches[-1])


if __name__ == "__main__":
    main()
