#!/usr/bin/env python3
"""Arnés de la UI (G22): arranca el initramfs base + un overlay con /harness.sh en qemu-system-arm (-M virt) y devuelve la consola.

Uso: [SHIMENV="WAIT=60 CVWAIT=0 ..."] run.py DIR_TRABAJO SCRIPT.sh [segundos] [extras_qemu...]
  Debe existir DIR_TRABAJO/{vmlinuz,base.cpio.gz} (lo crea setup.sh). El overlay se concatena (el kernel admite cpio.gz concatenados).
  SHIMENV se escribe en /cam/harness.env dentro del guest; im.sh lo exporta antes de arrancar im.elf.
"""
import base64
import gzip
import os
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
    if os.environ.get("SHIMENV"):
        (t / "cam/harness.env").write_text("export " + os.environ["SHIMENV"] + "\n")
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
    text = log.read_text(errors="replace")
    while "=====GUESTFILE-BEGIN" in text and "=====GUESTFILE-END" in text:  # ficheros extra (fb.bin…): gzip+base64 → DIR_TRABAJO/<nombre>
        pre, rest = text.split("=====GUESTFILE-BEGIN", 1)
        head, blob = rest.split("=====GUESTFILE-END", 1)[0].split("\n", 1)
        (work / head.strip()).write_bytes(gzip.decompress(base64.b64decode("".join(blob.split()))))
        text = pre + f"[{head.strip()} extraído]" + rest.split("=====GUESTFILE-END", 1)[1]
    if "=====GUESTLOG-BEGIN" in text and "=====GUESTLOG-END" in text:  # FULLLOG=1 en im.sh
        head, blob = text.split("=====GUESTLOG-BEGIN", 1)[1].split("=====GUESTLOG-END", 1)[0].split("\n", 1)
        raw = base64.b64decode("".join(blob.split()))
        data = gzip.decompress(raw) if "gzip" in head else raw
        (work / "guest.log").write_bytes(data)
        text = text.split("=====GUESTLOG-BEGIN", 1)[0] + f"[guest.log: {data.count(b'\n')} líneas]"
    print(text[-20000:])
