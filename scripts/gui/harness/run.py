#!/usr/bin/env python3
"""Arnés de la UI (G22): arranca el initramfs base + un overlay con /harness.sh en qemu-system-arm (-M virt) y devuelve la consola.

Uso: run.py DIR_TRABAJO SCRIPT.sh [segundos] [extras_qemu...]
  Debe existir DIR_TRABAJO/{vmlinuz,base.cpio.gz}. El overlay se concatena (el kernel admite cpio.gz concatenados).
"""
import shutil
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
    if (work / "overlay").is_dir():  # ficheros extra (p. ej. cam/usr/lib/sonyshim.so)
        shutil.copytree(work / "overlay", t, dirs_exist_ok=True)
    names = subprocess.run(["find", "cam"], cwd=t, capture_output=True, check=True).stdout
    cpio = subprocess.run(["cpio", "-o", "-H", "newc", "-R", "0:0", "--quiet"], input=names, cwd=t, capture_output=True, check=True).stdout
    initrd = t / "initrd.gz"
    gz = subprocess.run(["gzip", "-1"], input=cpio, capture_output=True, check=True).stdout
    initrd.write_bytes((work / "base.cpio.gz").read_bytes() + gz)
    cmd = ["qemu-system-arm", "-M", "virt", "-cpu", "cortex-a15", "-smp", "8", "-accel", "tcg,thread=multi", "-m", "1536", "-kernel", str(work / "vmlinuz"), "-initrd", str(initrd),
           "-append", "console=ttyAMA0 quiet loglevel=3", "-nographic", "-no-reboot", *extra]
    log = work / "last.log"
    with open(log, "wb") as out:
        p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        try:
            p.wait(timeout=secs)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
    print(log.read_text(errors="replace")[-20000:])
