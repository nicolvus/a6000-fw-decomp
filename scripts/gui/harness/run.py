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
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


def bk_patch(tbl: bytes, cambios: dict[int, bytes]) -> bytes:
    """bk.tbl ({id u32, len u32, datos rellenados a 4}*) con los registros de `cambios` sustituidos (o añadidos si no existían)."""
    out, o, vistos = bytearray(), 0, set()
    while o + 8 <= len(tbl):
        i, n = struct.unpack_from("<II", tbl, o)
        datos = cambios.get(i, tbl[o + 8:o + 8 + n])
        vistos.add(i)
        out += struct.pack("<II", i, len(datos)) + datos + b"\0" * (-len(datos) % 4)
        o += 8 + ((n + 3) & ~3)
    for i, datos in cambios.items():
        if i not in vistos:
            out += struct.pack("<II", i, len(datos)) + datos + b"\0" * (-len(datos) % 4)
    return bytes(out)


def build_initrd(work: Path, script: Path, t: Path, shimenv: str = "", overlay2: str = "", nvram: dict[int, bytes] | None = None) -> Path:
    """initrd = base.cpio.gz + cpio.gz con /cam/harness.sh, harness.env (SHIMENV), DIR/overlay y OVERLAY2; lo deja en t/initrd.gz.
    nvram = registros de backup cambiados por la UI (live.py): se aplican sobre /usr/share/bk.tbl de la copia, nunca sobre el volcado."""
    (t / "cam").mkdir()
    (t / "cam/harness.sh").write_text(script.read_text())
    (t / "cam/harness.sh").chmod(0o755)
    if shimenv:
        (t / "cam/harness.env").write_text("export " + shimenv + "\n")
    if (work / "overlay").is_dir():  # ficheros extra (p. ej. cam/usr/lib/sonyshim.so)
        shutil.copytree(work / "overlay", t, dirs_exist_ok=True)
    if overlay2:  # F5: /usr de un nflasha15 de CFW (pkg_usr.py); va después del base, así que sustituye a los de Sony
        shutil.copytree(overlay2, t, dirs_exist_ok=True)
    bk = t / "cam/usr/share/bk.tbl"
    if nvram and bk.exists():
        bk.write_bytes(bk_patch(bk.read_bytes(), nvram))
    names = subprocess.run(["find", "cam"], cwd=t, capture_output=True, check=True).stdout
    cpio = subprocess.run(["cpio", "-o", "-H", "newc", "-R", "0:0", "--quiet"], input=names, cwd=t, capture_output=True, check=True).stdout
    initrd = t / "initrd.gz"
    gz = subprocess.run(["gzip", "-1"], input=cpio, capture_output=True, check=True).stdout
    initrd.write_bytes((work / "base.cpio.gz").read_bytes() + gz)
    return initrd


def qemu_cmd(work: Path, initrd: Path, extra: list[str], console: list[str] | None = None) -> list[str]:
    ncpu = min(int(os.environ.get("QEMU_SMP", "8")), 8)  # el kernel netboot armmp de Debian trae NR_CPUS=8: más vCPU no se ven (medido: -smp 12 → 8 en /proc/cpuinfo)
    return ["qemu-system-arm", "-M", "virt", "-cpu", "cortex-a15", "-smp", str(ncpu), "-accel", "tcg,thread=multi,tb-size=512", "-m", "1536",
            "-kernel", str(work / "vmlinuz"), "-initrd", str(initrd), "-append", "console=ttyAMA0 quiet loglevel=3",
            *(console if console is not None else ["-nographic"]), "-no-reboot", *extra]


def main() -> None:
    work, script = Path(sys.argv[1]), Path(sys.argv[2])
    secs = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    res = Path(os.environ.get("HARNESS_OUT") or work)  # HARNESS_OUT: salidas propias (last.log, guest.log, extraídos) para varias VM en paralelo sobre el mismo DIR_TRABAJO
    res.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        initrd = build_initrd(work, script, Path(t), os.environ.get("SHIMENV", ""), os.environ.get("OVERLAY2", ""))
        log = res / "last.log"
        with open(log, "wb") as out:
            p = subprocess.Popen(qemu_cmd(work, initrd, sys.argv[4:]), stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            try:
                p.wait(timeout=secs)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
    text = log.read_text(errors="replace")
    while "=====GUESTFILE-BEGIN" in text and "=====GUESTFILE-END" in text:  # ficheros extra (fb.bin…): gzip+base64 → DIR_TRABAJO/<nombre>
        pre, rest = text.split("=====GUESTFILE-BEGIN", 1)
        head, blob = rest.split("=====GUESTFILE-END", 1)[0].split("\n", 1)
        (res / head.strip()).write_bytes(gzip.decompress(base64.b64decode("".join(blob.split()))))
        text = pre + f"[{head.strip()} extraído]" + rest.split("=====GUESTFILE-END", 1)[1]
    if "=====GUESTLOG-BEGIN" in text and "=====GUESTLOG-END" in text:  # FULLLOG=1 en im.sh
        head, blob = text.split("=====GUESTLOG-BEGIN", 1)[1].split("=====GUESTLOG-END", 1)[0].split("\n", 1)
        raw = base64.b64decode("".join(blob.split()))
        data = gzip.decompress(raw) if "gzip" in head else raw
        (res / "guest.log").write_bytes(data)
        text = text.split("=====GUESTLOG-BEGIN", 1)[0] + f"[guest.log: {data.count(b'\n')} líneas]"
    print(text[-20000:])


if __name__ == "__main__":
    main()
