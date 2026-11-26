#!/usr/bin/env python3
"""Arranque del arnés con el shim instrumentado (FILM-PB-1, sub-arnés-orden).

Construye el initrd como run.py/live.py (overlay del arnés + overlay propio con sonyshim.so +
cabeza FAT32 de la SD de ~/A6000-SD) y arranca qemu con la consola a fichero (-serial file:),
que es la forma en que live.py no pierde la salida del invitado. Al terminar, imprime las líneas
PBINJ/TRACE del registro y deja consola.log completo en SALIDA.

uso: python3 pb_run.py SEGUNDOS SALIDA [SHIMEXTRA]
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
H = REPO / "scripts/gui/harness"
sys.path.insert(0, str(H))
import run  # noqa: E402
import sd_emu  # noqa: E402
import sd_image  # noqa: E402
import live  # noqa: E402

TRACEFN2 = "437bc0,437bfa,437c0a,437c10,437c2c,437c3c,437c70,437d1a,437d2c,447810,44ee9c"


def main() -> None:
    secs = int(sys.argv[1])
    salida = Path(sys.argv[2]).resolve()
    extra = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("SHIMEXTRA", "")
    salida.mkdir(parents=True, exist_ok=True)
    work = REPO / "analysis/gui/g22/harness"
    overlay2 = REPO / "analysis/gui/g22/harness/live/pbo/overlay"
    shimenv = live.SHIMENV.replace(" LIVE=auto", "").replace("WAIT=999999", "WAIT=900")
    shimenv += (f" TRACELIB=libmpr.so TRACEFN2={TRACEFN2} TRACEREP=1 TRACEMAX=6"
                f" PBINJECT={os.environ.get('PBINJECT', '80')}"
                f"{' PBFORCE=1' if os.environ.get('PBFORCE') else ''} {extra}")
    consola = salida / "consola.log"
    consola.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cabeza = t / "sd.head"
        nsec = sd_image.construye(sd_emu.raiz_sd(""), cabeza, 4.0)
        print(f"[pb_run] SD {sd_emu.raiz_sd('')} -> {cabeza} ({nsec} sectores)", flush=True)
        initrd = run.build_initrd(work, HERE / "im_pb.sh", t, shimenv, str(overlay2), None, cabeza, None)
        cmd = run.qemu_cmd(work, initrd, [], ["-serial", f"file:{consola}", "-display", "none"])
        print("[pb_run] " + " ".join(cmd)[:300], flush=True)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while time.time() - t0 < secs and p.poll() is None:  # corta en cuanto el shim imprime el resultado
            time.sleep(2)
            if consola.exists() and "PBINJ FIN" in consola.read_text(errors="replace"):
                print(f"[pb_run] PBINJ FIN a los {time.time() - t0:.0f} s", flush=True)
                break
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
        print(f"[pb_run] qemu terminó a los {time.time() - t0:.0f} s (rc={p.returncode})", flush=True)
    texto = consola.read_text(errors="replace") if consola.exists() else ""
    print(f"[pb_run] consola.log: {len(texto)} B en {consola}", flush=True)
    for ln in texto.splitlines():
        if any(m in ln for m in ("PBINJ", "TRACE ", "IMEXIT", "alive=", "EXIT=")):
            print(ln[:220], flush=True)


if __name__ == "__main__":
    main()
