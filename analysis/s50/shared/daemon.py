#!/usr/bin/env python3
"""Demonio REA por instancia (S50). Uso: S50_NAME=claude|codex [S50_RSS_MAX_MB=8000] [GHIDRA_MAXMEM=4G] \
daemon.py ARGS_JSON_FILE. Socket/logs/tmp en analysis/s50/<NAME>/run. Cliente: analysis/rea-independent/bin/q.py SOCK guion.json."""
import sys, os, json, socket, time, threading, signal, fcntl
name = os.environ["S50_NAME"]
base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", name, "run")); os.makedirs(base + "/tmp", exist_ok=True)
for k in ("TMPDIR", "XDG_CACHE_HOME", "XDG_STATE_HOME", "XDG_DATA_HOME"): os.environ[k] = base + "/tmp"  # aislamiento por instancia
os.environ.setdefault("REA_GHIDRA_STARTUP_TIMEOUT_MS", "900000"); os.environ.setdefault("GHIDRA_MAXMEM", "4G")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../rea-independent/bin")); from mcpc import Mcp
sock_path = base + "/rea.sock"; open_args = json.load(open(sys.argv[1]))
idle_max, rss_max = int(os.environ.get("S50_IDLE_S", 14400)), int(os.environ.get("S50_RSS_MAX_MB", 8000))
LOG = open(base + "/session-log.jsonl", "a"); MET = open(base + "/metrics.csv", "a"); lock = threading.Lock(); last = [time.time()]
def mem(k): return int([l for l in open("/proc/meminfo") if l.startswith(k + ":")][0].split()[1]) // 1024
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
        time.sleep(10); r = rss_tree(os.getpid())
        MET.write(f"{int(time.time())},{r:.0f},{mem('MemAvailable')},{mem('SwapTotal')-mem('SwapFree')}\n"); MET.flush()  # ts,rss_MB,avail_MB,swap_used_MB
        if time.time() - last[0] > idle_max or r > rss_max or mem("MemAvailable") < 1000:  # protección: no agotar el equipo
            LOG.write(json.dumps({"event": "watchdog_exit", "rss_mb": r}) + "\n"); LOG.flush(); os.kill(os.getpid(), signal.SIGTERM)
MET.write("ts,rss_mb,mem_available_mb,swap_used_mb\n"); threading.Thread(target=watchdog, daemon=True).start()
m = Mcp(); t0 = time.time()
with open(os.path.join(base, "..", "..", "shared", "cold.lock"), "w") as lk:  # escalona los análisis en frío (picos de RAM)
    fcntl.flock(lk, fcntl.LOCK_EX); t1 = time.time()
    r = m.call("open_binary", open_args); r = m.call("inspect_native_load_image", {}, 3600)
LOG.write(json.dumps({"event": "analysis_ready", "wait_lock_s": round(t1 - t0, 1), "cold_s": round(time.time() - t1, 1)}) + "\n"); LOG.flush()
if os.path.exists(sock_path): os.unlink(sock_path)
srv = socket.socket(socket.AF_UNIX); srv.bind(sock_path); srv.listen(4); open(sock_path + ".ready", "w").write("ok")
def term(*_): m.close(); sys.exit(0)
signal.signal(signal.SIGTERM, term)
while True:
    c, _ = srv.accept(); last[0] = time.time(); data = b""
    while not data.endswith(b"\n"): data += c.recv(65536)
    req = json.loads(data)
    if req.get("shutdown"): c.sendall(b'{"bye":true}\n'); c.close(); term()
    for call in req["calls"]:
        with lock: out = m.call(call["tool"], call.get("args", {}), 1800)
        rec = dict(call=call, **out); LOG.write(json.dumps(rec) + "\n"); LOG.flush(); c.sendall((json.dumps(rec) + "\n").encode())
    c.close()
