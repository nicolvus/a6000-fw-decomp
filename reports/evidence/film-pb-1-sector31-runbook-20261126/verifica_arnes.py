#!/usr/bin/env python3
"""Verificación EN SECO de scripts/film_pb1_sector31.py contra el invitado del arnés (G22).

Arranca QEMU con el perfil `nf4` (NFLASH4=1: /dev/nflasha4 = copia real del volcado del 20-10) y
telnet del invitado en 127.0.0.1:2323 (hostfwd → 23, `busybox telnetd` del propio firmware, igual
que el Tweak). NO precarga /usr/lib/nf4inject.so: la inyección de consola ya no hace falta (las dos
líneas entran desde fuera con ptrace) y además ejecutaría InitB por su cuenta, contaminando el «antes».

Ejecuta, en este orden:
  1. scripts/film_pb1_sector31.py --verifica                    (sólo lectura)
  2. scripts/film_pb1_sector31.py --aplica                      (en seco: plan)
  3. scripts/film_pb1_sector31.py --aplica --escribe --origen-volcado /nflasha4.img --destino /tmp
     (en el invitado: volcado a /tmp, subida de ptcall, dos líneas al anillo, relectura del idx 10)

Cada salida queda en este directorio (*.out) y la consola del invitado en consola.log.
Uso: python3 reports/evidence/film-pb-1-sector31-runbook-20261126/verifica_arnes.py [segundos_max]
"""
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
H = REPO / "scripts/gui/harness"
sys.path.insert(0, str(H))

VOLCADO = REPO / "analysis/camera-dumps/nand-20261020/dev_nflasha4.bin"
PUERTO = 2323
os.environ["LIVE_NFLASH4"] = str(VOLCADO)
import live
import run
import sd_emu
import sd_image


def telnet_arriba(segundos: float) -> bool:
    t0 = time.time()
    while time.time() - t0 < segundos:
        try:
            socket.create_connection(("127.0.0.1", PUERTO), timeout=2).close()
            return True
        except OSError:
            time.sleep(3)
    return False


def im_elf_arriba() -> bool:
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from camera_telnet import run as telnet
        return bool(telnet("127.0.0.1", ["pidof im.elf"], port=PUERTO, timeout=10)[0].strip())
    except (OSError, IndexError):  # el invitado aún no contesta
        return False


def paso(nombre: str, args: list[str]) -> int:
    print(f"\n[verifica] === {nombre} ===", flush=True)
    p = subprocess.run([sys.executable, str(REPO / "scripts/film_pb1_sector31.py"), *args],
                       cwd=REPO, capture_output=True, text=True, check=False)
    texto = f"$ python3 scripts/film_pb1_sector31.py {' '.join(args)}\n{p.stdout}{p.stderr}"
    print(texto, flush=True)
    (HERE / f"{nombre}.out").write_text(texto)
    return p.returncode


def main() -> int:
    limite = float(sys.argv[1]) if len(sys.argv) > 1 else 420.0
    work = REPO / "analysis/gui/g22/harness"
    consola = HERE / "consola.log"
    consola.unlink(missing_ok=True)
    shimenv = live.SHIMENV.replace(" LIVE=auto", "").replace("WAIT=999999", "WAIT=1200") + " NET=telnet"
    net = ["-netdev", f"user,id=n0,hostfwd=tcp:127.0.0.1:{PUERTO}-:23",
           "-device", f"virtio-net-device,netdev=n0,mac={live.MAC_CAMARA}"]
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        cabeza = t / "sd.head"
        nsec = sd_image.construye(sd_emu.raiz_sd(""), cabeza, 4.0)
        print(f"[verifica] SD emulada: {nsec} sectores; nflasha4: {VOLCADO} ({VOLCADO.stat().st_size} B)",
              flush=True)
        initrd = run.build_initrd(work, H / "im.sh", t, shimenv, "", None, cabeza, VOLCADO)
        cmd = run.qemu_cmd(work, initrd, net, ["-serial", f"file:{consola}", "-display", "none"])
        if os.environ.get("VM_MEM"):  # el anfitrión va justo de RAM: -m 1024 QEMU_SMP=4
            cmd[cmd.index("-m") + 1] = os.environ["VM_MEM"]
        print("[verifica] " + " ".join(cmd)[:260], flush=True)
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rc = 1
        try:
            if not telnet_arriba(limite):
                print("[verifica] el telnet del invitado no abrió el puerto a tiempo", flush=True)
                return 1
            print(f"[verifica] telnet del invitado en 127.0.0.1:{PUERTO}", flush=True)
            while not im_elf_arriba():
                if p.poll() is not None:
                    print("[verifica] qemu terminó antes de arrancar im.elf", flush=True)
                    return 1
                time.sleep(5)
            print("[verifica] im.elf en marcha", flush=True)
            base = ["--host", "127.0.0.1", "--port", str(PUERTO)]
            rc1 = paso("1-aplica-seco", base + ["--aplica", "--origen-volcado", "/nflasha4.img",
                                                "--destino", "/tmp"])
            rc2 = paso("2-aplica-escribe", base + ["--aplica", "--escribe", "--origen-volcado",
                                                   "/nflasha4.img", "--destino", "/tmp"])
            rc3 = paso("3-verifica", base + ["--verifica"])
            rc = 0 if (rc1 == 1 and rc2 == 0 and rc3 == 0) else 1
            print(f"\n[verifica] códigos: seco={rc1} (1 esperado: no escribe) · escribe={rc2} "
                  f"(0 esperado) · verifica={rc3} (0 esperado)", flush=True)
        finally:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait()
            print(f"[verifica] qemu parado (rc={p.returncode}); consola: {consola}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
