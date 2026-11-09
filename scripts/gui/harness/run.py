#!/usr/bin/env python3
"""Arnés de la UI (G22): arranca el initramfs base + un overlay con /harness.sh en qemu-system-arm (-M virt) y devuelve la consola.

Uso: run.py DIR_TRABAJO SCRIPT.sh [segundos] [extras_qemu...]
  Debe existir DIR_TRABAJO/{vmlinuz,base.cpio.gz}. El overlay se concatena (el kernel admite cpio.gz concatenados).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

work, script = Path(sys.argv[1]), Path(sys.argv[2])
secs = int(sys.argv[3]) if len(sys.argv) > 3 else 120
extra = sys.argv[4:]
with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "cam").mkdir()
    (t / "cam/harness.sh").write_text(script.read_text())
    (t / "cam/harness.sh").chmod(0o755)
    cpio = subprocess.run(["cpio", "-o", "-H", "newc", "-R", "0:0", "--quiet"], input=b"cam\ncam/harness.sh\n", cwd=t, capture_output=True, check=True).stdout
    initrd = t / "initrd.gz"
    gz = subprocess.run(["gzip", "-1"], input=cpio, capture_output=True, check=True).stdout
    initrd.write_bytes((work / "base.cpio.gz").read_bytes() + gz)
    cmd = ["qemu-system-arm", "-M", "virt", "-cpu", "cortex-a15", "-m", "1536", "-kernel", str(work / "vmlinuz"), "-initrd", str(initrd),
           "-append", "console=ttyAMA0 quiet loglevel=3", "-nographic", "-no-reboot", *extra]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=secs, check=False)
        print(r.stdout[-20000:])
    except subprocess.TimeoutExpired as e:
        print((e.stdout or b"").decode(errors="replace")[-20000:] if e.stdout else "", "\n[timeout]")
