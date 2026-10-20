#!/usr/bin/env python3
"""Demonio REA portátil: una sesión MCP viva servida por TCP loopback.

Equivalente Windows/macOS/Linux de `analysis/rea-independent/bin/session_daemon.py`
(que es Linux-only: socket Unix, /proc y señales POSIX). Abre el binario una vez
(autoanálisis de Ghidra), y atiende lotes de llamadas MCP por JSONL.

    python scripts/agent/rea_daemon.py --binary <ruta> --args '{"path": "...", "base_address": "0x43541000"}'
    python scripts/agent/rea_client.py --calls guion.json [--daemon run/rea-win.json]

Variables: REA_NODE (node), REA_CLI (rea.mjs), REA_GHIDRA_STARTUP_TIMEOUT_MS,
GHIDRA_MAXMEM. El cliente lee el puerto de `analysis/rea-independent/run/rea-win.json`.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "analysis" / "rea-independent" / "run" / "rea-win.json"
DEFAULT_CLI = ROOT / "tools" / "rea" / "node_modules" / "rea-agents" / "scripts" / "rea.mjs"


class McpError(RuntimeError):
    pass


class Mcp:
    def __init__(self, node: str, cli: Path, log_path: Path):
        env = dict(os.environ)
        env.setdefault("REA_GHIDRA_STARTUP_TIMEOUT_MS", "900000")
        env.setdefault("GHIDRA_MAXMEM", "3G")
        self.proc = subprocess.Popen(
            [node, str(cli), "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=open(log_path, "a", encoding="utf-8"),
            text=True,
            bufsize=1,
            env=env,
        )
        self.responses: queue.Queue[dict] = queue.Queue()
        self.next_id = 0
        self.lock = threading.Lock()
        threading.Thread(target=self._reader, daemon=True).start()
        self.rpc(
            "initialize",
            {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "s63-daemon", "version": "1"}},
        )
        self.notify("notifications/initialized")

    def _reader(self):
        assert self.proc.stdout is not None
        for line in self.proc.stdout:
            try:
                self.responses.put(json.loads(line))
            except ValueError:
                continue

    def send(self, obj: dict):
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def notify(self, method: str, params: dict | None = None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        self.send(msg)

    def rpc(self, method: str, params: dict | None = None, timeout: float = 3600) -> dict:
        with self.lock:
            self.next_id += 1
            ident = self.next_id
            self.send({"jsonrpc": "2.0", "id": ident, "method": method, "params": params or {}})
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msg = self.responses.get(timeout=5)
            except queue.Empty:
                if self.proc.poll() is not None:
                    raise McpError("el servidor MCP terminó")
                continue
            if msg.get("id") == ident:
                return msg
        raise TimeoutError(method)

    def call(self, tool: str, args: dict, timeout: float = 3600) -> dict:
        started = time.time()
        result = self.rpc("tools/call", {"name": tool, "arguments": args}, timeout)
        result["_elapsed_s"] = round(time.time() - started, 2)
        return result

    def close(self):
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
            self.proc.wait(15)
        except Exception:
            self.proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--binary", required=True)
    ap.add_argument("--args", default="{}", help="argumentos JSON de open_binary")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--idle", type=int, default=3600)
    ap.add_argument("--node", default=os.environ.get("REA_NODE") or "node")
    ap.add_argument("--cli", default=os.environ.get("REA_CLI") or str(DEFAULT_CLI))
    ap.add_argument("--wait-tool", default="binary_overview", help="herramienta que fuerza el autoanálisis")
    ap.add_argument("--log", default=str(ROOT / "analysis" / "rea-independent" / "run" / "rea-win.log"))
    args = ap.parse_args()

    open_args = json.loads(args.args)
    open_args.setdefault("path", str(Path(args.binary).resolve()))
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log = (ROOT / "analysis" / "rea-independent" / "run" / "rea-win-session.jsonl").open("a", encoding="utf-8")
    started = time.time()
    mcp = Mcp(args.node, Path(args.cli), log_path)
    opened = mcp.call("open_binary", open_args)
    log.write(json.dumps({"event": "open_binary", "elapsed": opened.get("_elapsed_s")}) + "\n")
    ready = mcp.call(args.wait_tool, {}, 7200)  # bloquea hasta acabar la importación/autoanálisis
    cold = round(time.time() - started, 1)
    log.write(json.dumps({"event": "analysis_ready", "wait_tool": args.wait_tool, "cold_s": cold, "error": ready.get("error")}) + "\n")
    log.flush()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", args.port))
    srv.listen(4)
    port = srv.getsockname()[1]
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"port": port, "pid": os.getpid(), "binary": open_args["path"], "cold_s": cold, "started": started}) + "\n", encoding="utf-8")
    print(f"REA listo en 127.0.0.1:{port} (frío {cold}s) — {STATE}", flush=True)

    last = [time.time()]
    stop = threading.Event()

    def watchdog():
        while not stop.wait(10):
            if time.time() - last[0] > args.idle:
                log.write(json.dumps({"event": "watchdog_exit"}) + "\n")
                log.flush()
                os._exit(0)

    threading.Thread(target=watchdog, daemon=True).start()

    while True:
        conn, _ = srv.accept()
        last[0] = time.time()
        data = b""
        while not data.endswith(b"\n"):
            chunk = conn.recv(65536)
            if not chunk:
                break
            data += chunk
        try:
            request = json.loads(data)
        except ValueError:
            conn.close()
            continue
        if request.get("shutdown"):
            conn.sendall(b'{"bye": true}\n')
            conn.close()
            stop.set()
            mcp.close()
            STATE.unlink(missing_ok=True)
            return 0
        if request.get("list_tools"):
            result = mcp.rpc("tools/list")
            conn.sendall((json.dumps({"tools": result}) + "\n").encode())
            conn.close()
            continue
        out = []
        for call in request.get("calls", []):
            try:
                result = mcp.call(call["tool"], call.get("args", {}), call.get("timeout", 1800))
            except Exception as exc:  # el cliente decide; se registra y se sigue
                result = {"error": str(exc)}
            out.append(dict(call=call, **result))
            log.write(json.dumps(out[-1]) + "\n")
            log.flush()
        conn.sendall(("\n".join(json.dumps(o) for o in out) + "\n").encode())
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
