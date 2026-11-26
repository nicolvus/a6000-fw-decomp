#!/usr/bin/env python3
"""Arranca el arnés (perfil nf4: NFLASH4=1 + telnet del invitado en 127.0.0.1:2323) y lo deja vivo.

Igual que verifica_arnes.py pero sin ejecutar nada dentro: sirve para probar a mano por telnet
mientras la VM sigue en marcha. Se para con Ctrl-C o `tools.process.stop`.

Uso: python3 reports/evidence/film-pb-1-sector31-runbook-20261126/arranca_vm.py [segundos_max] [puerto]
"""
import os
import signal
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
H = REPO / "scripts/gui/harness"
sys.path.insert(0, str(H))

VOLCADO = REPO / "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin"
PUERTO = int(sys.argv[2]) if len(sys.argv) > 2 else 2323
os.environ["LIVE_NFLASH4"] = str(VOLCADO)
import live
import run
import sd_emu
import sd_image

sys.path.insert(0, str(REPO / "scripts"))
from camera_telnet import run as telnet


def sh(cmd: str) -> str:
    try:
        return telnet("127.0.0.1", [cmd], port=PUERTO, timeout=10)[0]
    except OSError:
        return ""


def main() -> int:
    limite = float(sys.argv[1]) if len(sys.argv) > 1 else 420.0
    work = REPO / "analysis/gui/g22/harness"
    consola = HERE / "consola.log"
    consola.unlink(missing_ok=True)
    shimenv = live.SHIMENV.replace(" LIVE=auto", "").replace("WAIT=999999", "WAIT=1800") + " NET=telnet"
    net = ["-netdev", f"user,id=n0,hostfwd=tcp:127.0.0.1:{PUERTO}-:23",
           "-device", f"virtio-net-device,netdev=n0,mac={live.MAC_CAMARA}"]
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cabeza = t / "sd.head"
        print(f"[vm] SD: {sd_image.construye(sd_emu.raiz_sd(''), cabeza, 4.0)} sectores", flush=True)
        initrd = run.build_initrd(work, H / "im.sh", t, shimenv, "", None, cabeza, VOLCADO)
        cmd = run.qemu_cmd(work, initrd, net, ["-serial", f"file:{consola}", "-display", "none"])
        if os.environ.get("VM_MEM"):  # el anfitrión va justo de RAM: -m 1024 QEMU_SMP=4
            cmd[cmd.index("-m") + 1] = os.environ["VM_MEM"]
        import subprocess
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[vm] qemu pid {p.pid}, telnet 127.0.0.1:{PUERTO}", flush=True)
        t0 = time.time()
        try:
            while time.time() - t0 < limite:
                if p.poll() is not None:
                    print("[vm] qemu terminó solo", flush=True)
                    return 1
                if "im.elf" in sh("pidof im.elf; ps | grep -c im.elf"):
                    print(f"[vm] im.elf en marcha a los {time.time() - t0:.0f} s", flush=True)
                    break
                time.sleep(5)
            print("[vm] LISTO (la VM sigue viva hasta que se pare este proceso)", flush=True)
            while p.poll() is None:
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
            print("[vm] parada", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
