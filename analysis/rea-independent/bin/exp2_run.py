#!/usr/bin/env python3
"""Ejecuta un guion MCP con vigilancia de tiempo y memoria. Uso: exp2_run.py guion.json salida.jsonl recursos.csv MAX_S MAX_RSS_MB"""
import sys, os, time, subprocess, signal, threading
script, outp, csvp, max_s, max_rss = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
here = os.path.dirname(os.path.abspath(__file__))
env = dict(os.environ, REA_GHIDRA_STARTUP_TIMEOUT_MS="900000", GHIDRA_MAXMEM="3G")
p = subprocess.Popen([sys.executable, f"{here}/mcpc.py", script], stdout=open(outp, "w"), stderr=open(outp + ".stderr", "w"), env=env, start_new_session=True)
def tree_rss(root):
    kids = {}; rss = {}
    for d in os.listdir("/proc"):
        if d.isdigit():
            try:
                st = open(f"/proc/{d}/stat").read().rsplit(") ", 1)[1].split()
                kids.setdefault(int(st[1]), []).append(int(d)); rss[int(d)] = int(st[21]) * 4096
            except Exception: pass
    tot, stack = 0, [root]
    while stack:
        x = stack.pop(); tot += rss.get(x, 0); stack += kids.get(x, [])
    return tot / 1048576
def avail():
    for l in open("/proc/meminfo"):
        if l.startswith("MemAvailable"): return int(l.split()[1]) / 1024
t0 = time.time(); reason = "finished"
with open(csvp, "w") as c:
    c.write("t_s,rss_mb,mem_available_mb\n")
    while p.poll() is None:
        r, a, t = tree_rss(p.pid), avail(), time.time() - t0
        c.write(f"{t:.0f},{r:.0f},{a:.0f}\n"); c.flush()
        if t > max_s: reason = "TIMEOUT_BUDGET"
        elif r > max_rss: reason = "RSS_LIMIT"
        elif a < 400: reason = "MEM_AVAILABLE_LOW"
        if reason != "finished":
            os.killpg(p.pid, signal.SIGTERM); time.sleep(5)
            if p.poll() is None: os.killpg(p.pid, signal.SIGKILL)
            break
        time.sleep(10)
print(f"reason={reason} elapsed={time.time()-t0:.0f}s rc={p.poll()}")
