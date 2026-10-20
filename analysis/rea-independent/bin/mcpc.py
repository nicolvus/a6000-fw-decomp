#!/usr/bin/env python3
"""Cliente MCP stdio mínimo para `scripts/rea mcp` (sin dependencias).
Uso: mcpc.py LISTA_JSON_DE_LLAMADAS  -> escribe resultados JSONL en stdout.
Cada llamada: {"tool": "...", "args": {...}}; "tools/list" imprime esquemas."""
import json, subprocess, sys, time, os, select

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

class Mcp:
    def __init__(self, env_extra=None, cwd=None):
        env = dict(os.environ, **(env_extra or {}))
        self.p = subprocess.Popen([f"{ROOT}/scripts/rea", "mcp"], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=cwd, text=True, bufsize=1)
        self.n = 0
        self.rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                "clientInfo": {"name": "rea-independent", "version": "1"}})
        self.notify("notifications/initialized")

    def send(self, o): self.p.stdin.write(json.dumps(o) + "\n"); self.p.stdin.flush()
    def notify(self, m, params=None): self.send({"jsonrpc": "2.0", "method": m, **({"params": params} if params else {})})
    def rpc(self, m, params=None, timeout=3600):
        self.n += 1; i = self.n
        self.send({"jsonrpc": "2.0", "id": i, "method": m, "params": params or {}})
        end = time.time() + timeout
        while time.time() < end:
            r, _, _ = select.select([self.p.stdout], [], [], 5)
            if not r: continue
            line = self.p.stdout.readline()
            if not line: raise RuntimeError("servidor MCP terminó")
            try: msg = json.loads(line)
            except ValueError: continue
            if msg.get("id") == i: return msg
        raise TimeoutError(m)
    def call(self, tool, args, timeout=3600):
        t = time.time(); r = self.rpc("tools/call", {"name": tool, "arguments": args}, timeout)
        r["_elapsed_s"] = round(time.time() - t, 2); return r
    def close(self):
        try: self.p.stdin.close(); self.p.wait(15)
        except Exception: self.p.kill()

if __name__ == "__main__":
    m = Mcp()
    try:
        for c in json.load(open(sys.argv[1])):
            if c["tool"] == "tools/list": print(json.dumps(m.rpc("tools/list")))
            else: print(json.dumps(dict(call=c, **m.call(c["tool"], c.get("args", {})))), flush=True)
    finally: m.close()
