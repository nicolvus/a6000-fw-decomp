#!/usr/bin/env python3
"""Mantiene UNA sesión REA/Ghidra abierta y atiende llamadas MCP por socket Unix (workaround de rea#1048).
Uso: session_daemon.py SOCK BINARIO_JSON_ARGS  |  cliente: q.py SOCK guion.json"""
import sys, os, json, socket, time, threading, signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcpc import Mcp
sock_path, open_args, idle_max = sys.argv[1], json.loads(sys.argv[2]), 3600
rss_max = int(os.environ.get("REA_DAEMON_RSS_MAX_MB", "3800"))  # salvaguarda anti-OOM; ampliable por entorno
os.environ.setdefault("REA_GHIDRA_STARTUP_TIMEOUT_MS", "900000"); os.environ.setdefault("GHIDRA_MAXMEM", "3G")
m = Mcp(); last = [time.time()]; lock = threading.Lock()
LOG = open(os.path.join(os.path.dirname(sock_path), "../out/exp2-session-log.jsonl"), "a")
def rss_tree(root):
    kids, rss = {}, {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try: st = open(f"/proc/{d}/stat").read().rsplit(") ", 1)[1].split(); kids.setdefault(int(st[1]), []).append(int(d)); rss[int(d)] = int(st[21]) * 4096
            except Exception: pass
    t, s = 0, [root]
    while s: x = s.pop(); t += rss.get(x, 0); s += kids.get(x, [])
    return t / 1048576
def watchdog():
    while True:
        time.sleep(10)
        if time.time() - last[0] > idle_max or rss_tree(os.getpid()) > rss_max:
            LOG.write(json.dumps({"event": "watchdog_exit"}) + "\n"); LOG.flush(); os.kill(os.getpid(), signal.SIGTERM)
threading.Thread(target=watchdog, daemon=True).start()
t0 = time.time(); r = m.call("open_binary", open_args); print("open", r["_elapsed_s"], flush=True)
r = m.call("inspect_native_load_image", {}, 3600)  # bloquea hasta que el autoanálisis termina
LOG.write(json.dumps({"event": "analysis_ready", "cold_s": round(time.time() - t0, 1)}) + "\n"); LOG.flush()
if os.path.exists(sock_path): os.unlink(sock_path)
srv = socket.socket(socket.AF_UNIX); srv.bind(sock_path); srv.listen(4)
open(sock_path + ".ready", "w").write(str(round(time.time() - t0, 1)))
def term(*_): m.close(); sys.exit(0)
signal.signal(signal.SIGTERM, term)
while True:
    c, _ = srv.accept(); last[0] = time.time()
    data = b""
    while not data.endswith(b"\n"): data += c.recv(65536)
    req = json.loads(data)
    if req.get("shutdown"): c.sendall(b'{"bye":true}\n'); c.close(); term()
    for call in req["calls"]:
        with lock: out = m.call(call["tool"], call.get("args", {}), 1800)
        rec = dict(call=call, **out); LOG.write(json.dumps(rec) + "\n"); LOG.flush()
        c.sendall((json.dumps(rec) + "\n").encode())
    c.close()
