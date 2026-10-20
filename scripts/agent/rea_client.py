#!/usr/bin/env python3
"""Cliente del demonio REA portátil (`scripts/agent/rea_daemon.py`).

    python scripts/agent/rea_client.py --tools
    python scripts/agent/rea_client.py --calls guion.json [--out salida.jsonl]
    python scripts/agent/rea_client.py --shutdown

`guion.json` es una lista `[{"tool": "...", "args": {...}, "timeout": 600}]`.
El puerto se lee de `analysis/rea-independent/run/rea-win.json`.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "analysis" / "rea-independent" / "run" / "rea-win.json"


def send(port: int, payload: dict, timeout: float = 7200) -> list[dict]:
    with socket.create_connection(("127.0.0.1", port), timeout=30) as sock:
        sock.settimeout(timeout)
        sock.sendall((json.dumps(payload) + "\n").encode())
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(1 << 20)
            if not chunk:
                break
            data += chunk
    return [json.loads(line) for line in data.decode().splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls")
    ap.add_argument("--tools", action="store_true")
    ap.add_argument("--shutdown", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--port", type=int)
    ap.add_argument("--daemon", default=str(STATE))
    args = ap.parse_args()

    port = args.port
    if port is None:
        state = json.loads(Path(args.daemon).read_text(encoding="utf-8"))
        port = state["port"]

    if args.shutdown:
        print(json.dumps(send(port, {"shutdown": True}, 60)))
        Path(args.daemon).unlink(missing_ok=True)
        return 0
    if args.tools:
        out = send(port, {"list_tools": True})
    else:
        calls = json.loads(Path(args.calls).read_text(encoding="utf-8"))
        out = send(port, {"calls": calls})

    text = "\n".join(json.dumps(o) for o in out)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
