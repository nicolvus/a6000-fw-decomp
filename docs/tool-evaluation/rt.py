#!/usr/bin/env python3
"""Ejecuta un comando con timeout; registra tiempo, rc y salida en results/ (JSONL + log)."""
import json, subprocess, sys, time
from pathlib import Path

out = Path(__file__).parent / "results"
label, timeout, *cmd = sys.argv[1:]
t0 = time.monotonic()
try:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=int(timeout), stdin=subprocess.DEVNULL)
    rc, so, se = p.returncode, p.stdout, p.stderr
except subprocess.TimeoutExpired as e:
    rc, so, se = "timeout", (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT"
dt = round(time.monotonic() - t0, 2)
(out / f"{label}.log").write_text(f"$ {' '.join(cmd)}\n--- stdout\n{so}\n--- stderr\n{se}\n")
with (out / "results.jsonl").open("a") as f:
    f.write(json.dumps({"label": label, "cmd": " ".join(cmd), "rc": rc, "seconds": dt}) + "\n")
print(f"[{label}] rc={rc} {dt}s")
sys.stdout.write("\n".join((so + se).splitlines()[:int(__import__('os').environ.get('SHOW', '8'))]) + "\n")
